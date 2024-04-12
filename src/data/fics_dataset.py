import requests
import functools
import pathlib
import shutil
import requests
from tqdm.auto import tqdm
import os
import bz2
import os
import re
import pandas as pd
from typing import List
import logging
import zipfile

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

class FICSDatasetBuilder(object):

    SPLIT_WIDTH=10000
    games_mapping={
        "standard":3,
        "blitz":5,
        "lightning":7,
        "player":11,
    }
    def __init__(self,base_dir:str,game_type:str,years:List[int]):
        self._base_dir=base_dir
        self._game_type=game_type
        self._years=years
        self._logger = logging.getLogger(__name__)
        self._logger.info('Initializing FICSDatasetBuilder')

    def __get_link(self,year,game_type,player=''):
        """ Returns a link for file to download
        """
 
        self._logger.info(f'Getting link for year {year} for game type:{game_type} for :{player}')
        'gametype=11&player=lotfour&year=2023&month=0&movetimes=0&download=Download'
        url = 'https://www.ficsgames.org/cgi-bin/download.cgi'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.ficsgames.org',
            'Referer': 'https://www.ficsgames.org/download.html',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"'
        }
        data = {
            'gametype': FICSDatasetBuilder.games_mapping[game_type],
            'player': player,
            'year': year,
            'month': '0',
            'movetimes': '0',
            'download': 'Download'
        }

        response = requests.post(url, headers=headers, data=data)
        text=response.text
        text = text.split("The requested games can be downloaded from here")[1]
        text=text[text.index("<"):text.index(">")]
        text=text[text.index("=")+1:].replace('"', '')

        return "https://www.ficsgames.org/"+text


    def __download(self,url, filename,player_name=None):
        self._logger.info(f'Downloading from {url}')

        r = requests.get(url, stream=True, allow_redirects=True)

        if r.status_code != 200:
            print(r.status_code)
            r.raise_for_status()  # Will only raise for 4xx codes, so...
            raise RuntimeError(f"Request to {url} returned status code {r.status_code}")
        file_size = int(r.headers.get('Content-Length', 0))

        path = pathlib.Path(filename).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        desc = "(Unknown total file size)" if file_size == 0 else ""
        r.raw.read = functools.partial(r.raw.read, decode_content=True)  # Decompress if needed
        with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc) as r_raw:
            with path.open("wb") as f:
                shutil.copyfileobj(r_raw, f)

        return path
    def __create_folders(self,year,player_name=None):
        self._logger.info(f'Creating folders')
        if not os.path.exists(f'{self._base_dir}/data'):
            os.mkdir(f'{self._base_dir}/data')

        if not os.path.exists(f'{self._base_dir}/data/fics-build/'):
            os.mkdir(f'{self._base_dir}/data/fics-build/')

        if not os.path.exists(f'{self._base_dir}/data/fics-build/raw'):
            os.mkdir(f'{self._base_dir}/data/fics-build/raw')
        if not os.path.exists(f'{self._base_dir}/data/fics-build/raw'):
            os.mkdir(f'{self._base_dir}/data/fics-build/raw')

        if not os.path.exists(f'{self._base_dir}/data/fics-build/raw/{year}'):
            os.mkdir(f'{self._base_dir}/data/fics-build/raw/{year}')
        if not os.path.exists(f'{self._base_dir}/data/fics-build/interim'):
            os.mkdir(f'{self._base_dir}/data/fics-build/interim')
        if not os.path.exists(f'{self._base_dir}/data/fics-build/proccessed'):
            os.mkdir(f'{self._base_dir}/data/fics-build/proccessed')
        
        if player_name is not None:
            if not os.path.exists(f'{self._base_dir}/data/fics-build/raw/{year}/{player_name}'):
                os.mkdir(f'{self._base_dir}/data/fics-build/raw/{year}/{player_name}')
            if not os.path.exists(f'{self._base_dir}/data/fics-build/proccessed/{player_name}'):
                os.mkdir(f'{self._base_dir}/data/fics-build/proccessed/{player_name}')
            if not os.path.exists(f'{self._base_dir}/data/fics-build/interim/{player_name}'):
                os.mkdir(f'{self._base_dir}/data/fics-build/interim/{player_name}')



    def __download_games_fics(self,year,game_type,player_name=None):
        url = self.__get_link(year,game_type,player_name)
        print(url)
        if player_name is None:
            self.__download(url,f'{self._base_dir}/data/fics-build/raw/{year}/ficsgamesdb_{game_type}.pgn.bz2')
            return f'{self._base_dir}/data/fics-build/raw/{year}/ficsgamesdb_{game_type}.pgn.bz2'
        else:
            self.__download(url,f'{self._base_dir}/data/fics-build/raw/{year}/{player_name}/ficsgamesdb_{game_type}.pgn.zip',player_name)
            self._logger.info(f'Done')

            return f'{self._base_dir}/data/fics-build/raw/{year}/{player_name}/ficsgamesdb_{game_type}.pgn.zip'

    def __extract_content(self,input_file,output_file,f_type='bz2'):

        if f_type=='bz2':
            self._logger.info(f'Extracting the content of {input_file} to {output_file}')
            with bz2.open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
                f_out.write(f_in.read())
            self._logger.info(f'Done ')
        else:
            self._logger.info(f'Extracting the content of {input_file} to {output_file} for player')
            with zipfile.ZipFile(input_file,"r") as zip_ref:
                zip_ref.extractall(output_file)
            self._logger.info(f'Done for player')



    def __get_seperators(self,lines):
        starters=[]
        for i in range(len(lines)):
            if "Event" in lines[i]:
                starters.append(i)
        return starters


    def __extract_game(self,lines,save_move=True):
        game={}
        moves=[]
        for line in lines:
            if "[Event" in line:
                game["Event"]=[(line.replace("Event","")[1:-1])]
            elif "[FICSGamesDBGameNo" in line:
                game["FICSGamesDBGameNo"]=[(line.replace("FICSGamesDBGameNo","")[1:-1])]
            elif "[WhiteIsComp" in line:
                game["WhiteIsComp"]=[(line.replace("WhiteIsComp","")[1:-1])]
            elif "[BlackIsComp" in line:
                game["BlackIsComp"]=[(line.replace("BlackIsComp","")[1:-1])]
            elif "[TimeControl" in line:
                game["TimeControl"]=[(line.replace("TimeControl","")[1:-1])]
            elif "[WhiteRatingDiff" in line:
                game["WhiteRatingDiff"]=[(line.replace("WhiteRatingDiff","")[1:-1])]
            elif "[BlackRatingDiff" in line:
                game["BlackRatingDiff"]=[(line.replace("BlackRatingDiff","")[1:-1])]
            elif "[BlackClock" in line:
                game["BlackClock"]=[(line.replace("BlackClock","")[1:-1])]
            elif "[WhiteClock" in line:
                game["WhiteClock"]=[(line.replace("WhiteClock","")[1:-1])]
            elif "[Result" in line:
                game["Result"]=[(line.replace("Result","")[1:-1])]
            elif "[UTCDate" in line:
                game["UTCDate"]=[(line.replace("UTCDate","")[1:-1])]
            elif "[UTCTime" in line:
                game["UTCTime"]=[(line.replace("UTCTime","")[1:-1])]
            elif "[WhiteElo" in line:
                game["WhiteElo"]=[(line.replace("WhiteElo","")[1:-1])]
            elif "[BlackElo" in line:
                game["BlackElo"]=[(line.replace("BlackElo","")[1:-1])]
            elif "[Opening" in line:
                game["Opening"]=[(line.replace("Opening","")[1:-1])]
            elif "[Site" in line:
                game["Site"]=[(line.replace("Site","")[1:-1])]
            elif "[Termination" in line:
                game["Termination"]=[(line.replace("Termination","")[1:-1])]
            elif "[PlyCount" in line:
                game["PlyCount"]=[(line.replace("PlyCount","")[1:-1])]
            elif "[Time" in line:
                game["Time"]=[(line.replace("Time","")[1:-1])]
            elif "[Date" in line:
                game["Date"]=[(line.replace("Date","")[1:-1])]
            elif "[BlackRD" in line:
                game["BlackRD"]=[(line.replace("BlackRD","")[1:-1])]
            elif "[WhiteRD" in line:
                game["WhiteRD"]=[(line.replace("WhiteRD","")[1:-1])]
            elif "[Black " in line:
                game["Black"]=[(line.replace("Black","")[1:-1])]
            elif "[White " in line:
                game["White"]=[(line.replace("White","")[1:-1])]
            elif "[ECO" in line:
                game["ECO"]=[(line.replace("ECO","")[1:-1])]
            elif len(line)==0:
                pass
            elif len(re.split(r'\d+\.', line))>0:
                parts = re.split(r'\d+\.', line)
                moves=moves+parts
            else:
                print(line)

        for k in game.keys():
            game[k]=[game[k][0].replace("\"","")[1:]]
        if save_move:
            game["Move"]=["|".join(moves)]
        return pd.DataFrame.from_dict(game)

    def __merge_parts(self,src_dir,dst):
        self._logger.info(f'Merging parts located at {src_dir} tp {dst}')

        if os.path.isdir(self._base_dir+"/data/fics-build/raw/"+src_dir):
            all_csv_files=[f for f in os.listdir(self._base_dir+"/data/fics-build/raw/"+src_dir) if ".csv" in f ]
            frames=[]
            self._logger.info("Loading files")
            for src_file in tqdm(all_csv_files):
                frames.append(pd.read_csv(self._base_dir+"/data/fics-build/raw/"+src_dir+"/"+src_file))
            self._logger.info("merging files")
            result = pd.concat(frames)
            result.to_csv(self._base_dir+"/data/fics-build/interim/"+dst)
            self._logger.info("deleting original files")
            for src_file in tqdm(all_csv_files):
                os.remove(self._base_dir+"/data/fics-build/raw/"+src_dir+"/"+src_file)
    def __split_to_parts(self,file_path):
        with open(file_path) as f:
            data=f.read()
            lines=data.split("\n")
            starters=self.__get_seperators(lines)
            frames=[]

            c=0
            for i in tqdm(range(1,len(starters))):
                frames.append(self.__extract_game(lines[starters[i-1]:starters[i]]))
                if len(frames)>FICSDatasetBuilder.SPLIT_WIDTH:
                    pd.concat(frames).to_csv(file_path.replace(".pgn",f"-{c}.csv"))
                    frames=[]
                    c=c+1    

            pd.concat(frames).to_csv(file_path.replace(".pgn",f"-{c}.csv"))
    def __convert_pgn_to_csv(self,file_path):
        self._logger.info(f'Converting pgn to csv ')
        print(file_path)
        with open(file_path) as f:
            data=f.read()
            lines=data.split("\n")
            starters=self.__get_seperators(lines)
            frames=[]
            for i in tqdm(range(1,len(starters))):
                frames.append(self.__extract_game(lines[starters[i-1]:starters[i]]))
            pd.concat(frames).to_csv(file_path.replace(".pgn",f".csv"))
        self._logger.info(f'Done ')


    def download_per_player(self,player_name):
        all_files=[]
        for year in self._years:
            try:
                link=self.__get_link(year,self._game_type,player_name)
                print(link)
                self.__create_folders(year,player_name)

                input_file=self.__download_games_fics(year,self._game_type,player_name)
                output_file=input_file.replace(".zip","")
                print(output_file)
                output_dir=output_file[0:output_file.rindex("/")]

                self.__extract_content(input_file,output_dir,'zip')
                output_file=[f for f in os.listdir(output_dir) if ".zip" not in f][0]

                self.__convert_pgn_to_csv(output_dir+"/"+output_file)
                all_files.append(output_dir+"/"+output_file.replace(".pgn",f".csv"))
                print(output_dir+"/"+output_file.replace(".pgn",f".csv"))

            except Exception as err:
                print(err)
                pass
        print(all_files)
        frames=[pd.read_csv(f) for f in tqdm(all_files)]
        pd.concat(frames).to_csv(self._base_dir+f"/data/fics-build/proccessed/{player_name}/chess-games.csv")
        for path in all_files:
            os.remove(path)
 

    def build(self):
        self._logger.info(f'Building dataset')
        for year in self._years:
            self._logger.info(f'Building {year}')
            self.__create_folders(year)
            input_file=self.__download_games_fics(year,self._game_type)
            output_file=input_file.replace(".bz2","")
            
            self.__extract_content(input_file,output_file)
            self.__split_to_parts(output_file)
            self.__merge_parts(str(year),str(year)+".csv")
            os.remove(input_file)
            os.remove(output_file)

        self._logger.info(f'Creating merged content')
        all_csv_files=[f for f in os.listdir(self._base_dir+"/data/fics-build/interim/") if ".csv" in f ]
        frames=[pd.read_csv(self._base_dir+"/data/fics-build/interim/"+fname) for fname in tqdm(all_csv_files)]
        pd.concat(frames).to_csv(self._base_dir+"/data/fics-build/proccessed/chess-games.csv")
        full_paths=[self._base_dir+"/data/fics-build/interim/"+fname for fname in tqdm(all_csv_files)]
        for path in full_paths:
            os.remove(path)


xdata-nba
=========

Tools to mine NBA data

Information:

com.soteradefense.xdata.xdata.py (xdata.py) is the driver for the whole project. Most of the remaining scripts use data that is provided by this script. The xdata.py script pulls from 'stats.nba.com'.
Within xdata.py you may need to set the variable 'currentGameId' to the beginning of the season you wish to capture. See the comments in the file for more detail. The script will create a Game.ID file
which holds the last ID the script was trying to capture. This will be useful when pulling incomplete information from a season. It will allow you to rerun the script in the future and pickup with the 
last game attempted.

Recommend script execution order:

1) xdata.py
2) espn.py (for 2013 season and up), espn_jquery.py for (2010 season to 2012)
3) yahoo.py (for 2013 season and up)
4) xdata.py (you should only have to run this script once as the team names and IDs shouldn't change often)

Once you have retrieved all the data for a season you can run the transformation scripts to create files that can be loaded into HIVE tables, order is not important.

*) transformer_game_commentary.py

*) transformer_game_comments.py

*) transformer_game_play_by_play.py

*) transformer_game_player_stats.py

*) transformer_game_players.py

*) transformer_game_stats.py

*) transformer_team_data.py

The file 'xdata_nba_load.sh' is a shell script used to create the Hive database, stage the data in HDFS, and load the staged data into Hive.

Execute ./xdata_nba_load.sh -h for more information.

Currently the data is written to <project_root>/output/

Logs are written to <project_root>/

Hive files are written to <project_root>/
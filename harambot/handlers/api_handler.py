from typing import List, Optional, Any, Dict
from abc import ABC, abstractmethod

class APIHandler(ABC):

    @abstractmethod
    def get_standings(self, guild_id: int) -> (str, List[Dict[str, Any]]):
        """Returns the current standings of the league."""
        pass

    @abstractmethod
    def get_teams(self, guild_id: int) -> Dict[str, Any]:
        """Returns the teams in the league."""
        pass

    @abstractmethod
    def roster_check(self, guild_id) -> bool:
        """Returns true if the roster command is supported, false if not"""
        pass

    @abstractmethod
    def get_roster(self, team_name: str, guild_id: int) -> List[Dict[str, Any]]:
        """Returns the roster of the given team."""
        pass

    @abstractmethod
    def trade_check(self, guild_id) -> bool:
        """Returns true if the trade command is supported, false if not"""
        pass

    @abstractmethod
    def get_latest_trade(self, guild_id: int) -> str:
        """Returns the latest accepted trade for the league."""
        pass
    
    @abstractmethod
    def get_players(self, player_name: str, guild_id: int) -> List[Dict[str, Any]]:
        """Returns details for players matching the given name."""
        pass

    @abstractmethod
    def get_player_details(
        self, player_name: str, guild_id: int, week: Optional[int] = None
    ) -> Dict[str, Any]:
        """Returns the details of a given player, including stats for a specific week or season."""
        pass

    @abstractmethod
    def matchups_check(self, guild_id) -> bool:
        """Returns true if the matchups command is supported, false if not"""
        pass

    @abstractmethod
    def get_matchups(self, guild_id: int, week: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns the matchups for a given week."""
        pass
        
    @abstractmethod
    def get_transactions(self, guild_id: int, timestamp: float = 0.0) -> List[Dict[str, Any]]:
        """Returns the transactions for the league since the given timestamp."""
        pass


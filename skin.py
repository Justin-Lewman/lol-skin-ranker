class Skin:
    def __init__(self, skin_info):
        # Required fields
        self.ID = skin_info.get("id")
        self.Elo = skin_info.get("ELO")
        self.Uncertainty = skin_info.get("Uncertainty")
        self.Matches = skin_info.get("Matches")
        self.Champion = skin_info.get('champion', 'Unknown')
        self.Skin_Name = skin_info.get('skin_name', 'Unknown')
        self.Price = skin_info.get('price', 'Unknown')
        self.Release = skin_info.get('release_date', 'Unknown')
        self.Rarity = skin_info.get('rarity', 'Unknown')
        self.Availability = skin_info.get('availability', 'Unknown')
        self.Loot_findable = skin_info.get('loot_eligible', False)

        # Lists
        self.Universes = skin_info.get('universes', ['Runeterra'])
        self.Skinlines = skin_info.get('skinlines', ['Base'])
        if not self.Universes:
            self.Universes = ["Runeterra"]
        if not self.Skinlines:
            self.Skinlines = ["Base"]
        self.Chromas = skin_info.get('chromas', [])

        # Multimedia
        self.Splash = skin_info.get('splash', None)
        self.Loadscreen = skin_info.get('loadscreen', None)
        self.Videos = skin_info.get('videos', [])

        # Additional info
        self.Description = skin_info.get('description', f'https://universe.leagueoflegends.com/en_US/story/champion/{self.Champion}/')
        if not self.Description:
            self.Description = f'https://universe.leagueoflegends.com/en_US/story/champion/{self.Champion}/'
        self.New_Effects = skin_info.get('new_effects', False)
        self.New_Animations = skin_info.get('new_animations', False)
        self.New_Recall = skin_info.get('new_recall', False)
        self.New_Voice = skin_info.get('new_voice', False)
        self.New_Quotes = skin_info.get('new_quotes', False)

        # Create the dictionary for JSON output
        self.skin_data = dict()
        self.create_json_format()

    def create_json_format(self):
        self.skin_data = {
            "ID": self.ID,
            "ELO": self.Elo,
            "Uncertainty": self.Uncertainty,
            "Matches": self.Matches,
            "Champion": self.Champion,
            "Skin_Name": self.Skin_Name,
            "Price": self.Price,
            "Release": self.Release,
            "Rarity": self.Rarity,
            "Availability": self.Availability,
            "Loot_findable": self.Loot_findable,
            "Universes": self.Universes,
            "Skinlines": self.Skinlines,
            "Description": self.Description,
            "New_Effects": self.New_Effects,
            "New_Animations": self.New_Animations,
            "New_Recall": self.New_Recall,
            "New_Voice": self.New_Voice,
            "New_Quotes": self.New_Quotes,
            "Splash": self.Splash,
            "Loadscreen": self.Loadscreen,
            "Chromas": self.Chromas,
            "Videos": self.Videos
        }

    def to_dict(self):
        """Return the skin data as a Python dict for JSON serialization"""
        return self.skin_data

    def __str__(self):
        final_str = ""
        for k, v in self.skin_data.items():
            final_str += f"{k}: {v}\n"
        return final_str



class Skin:
    def __init__(self, name, skin_info):
        self.Skin_Name = name
        self.Champion = skin_info.get('Champion', 'Unknown')
        self.Price = skin_info.get('Price', 'Unknown')
        self.Release = skin_info.get('Release date', 'Unknown')
        self.Rarity = skin_info.get('Rarity', 'Unknown')
        self.Availability = skin_info.get('Availability', 'Unknown')
        self.Loot_findable = skin_info.get('Loot eligibility', 'Unknown')
        self.Universes = skin_info.get('Universes', 'Runeterra')
        self.Skinline = skin_info.get('Skinlines', 'Base')
        self.Splash_img = skin_info.get('Splash', 'Unknown')
        self.Animations_video = skin_info.get('Video', 'Unknown')
        # TODO deal with skin features
        self.Feature_list = skin_info.get('Feature_list', 'Unknown')
        self.skin_data = {}
        self.create_json_format()

    def create_json_format(self):
        self.skin_data = {
            "Champion": self.Champion,
            "Skin_Name": self.Skin_Name,
            "Price": self.Price,
            "Release": self.Release,
            "Rarity": self.Rarity,
            "Availability": self.Availability,
            "Loot_findable": self.Loot_findable,
            "Universes": self.Universes,
            "Skinline": self.Skinline,
            "Splash": self.Splash_img,
            "Animations": self.Animations_video
        }

    def __str__(self):
        final_str = f""
        for k,v in self.skin_data.items():
            final_str += f"{k}: {v}\n"
        return final_str

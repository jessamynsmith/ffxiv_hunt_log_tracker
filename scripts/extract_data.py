"""Parse raw FFXIV hunting log text (scraped from the wiki) into
data/hunting_log.json. Run this first; build_page.py and export_csv.py
both read its output.

Source: https://ffxiv.consolegameswiki.com/wiki/Hunting_Log and its nine
linked per-class pages, plus the three Grand Company pages (Maelstrom,
Order of the Twin Adder, Immortal Flames) (that overview page itself has
no entry data, only links out to each class's/company's own Hunting Log
page).
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = REPO_ROOT / "data" / "hunting_log.json"

# Raw data captured from WebFetch results, per class, per rank.
# Format markers vary by class; parsed individually below.

arcanist = {
1: """Little Ladybug -> Middle La Noscea (Zephyr Drift)
Wharf Rat -> Middle La Noscea (Zephyr Drift)
Lost Lamb -> Middle La Noscea (Zephyr Drift)
Wind Sprite -> Lower La Noscea (Cedarwood)
Puk Hatchling -> Middle La Noscea (Summerford)
Nesting Buzzard -> Lower La Noscea (Cedarwood)
Bogy -> Middle La Noscea (Summerford)
Cave Bat -> Lower La Noscea (Cedarwood)
Galago -> Lower La Noscea (Cedarwood)
Grounded Pirate -> Middle La Noscea (Summerford)
Lightning Sprite -> Lower La Noscea (The Gods' Grip)""",
2: """Sewer Mole -> Western La Noscea (Quarterstone)
Mossless Goobbue -> Middle La Noscea / Lower La Noscea
Fat Dodo -> Western La Noscea (Quarterstone)
Arbor Buzzard -> Western La Noscea (Quarterstone)
Qiqirn Eggdigger -> Lower La Noscea (The Gods' Grip)
Dusk Bat -> Western La Noscea (Skull Valley)
Puk Hatchling -> Western La Noscea (Skull Valley)
Hedgemole -> Western La Noscea (Skull Valley)
Rothlyt Pelican -> Western La Noscea (Skull Valley)
Killer Mantis -> Western La Noscea (Skull Valley)
Bumble Beetle -> Upper La Noscea (Oakwood)""",
3: """Overgrown Ivy -> East Shroud (Nine Ivies)
Lead Coblyn -> Western Thanalan (The Footfalls)
Kedtrap -> South Shroud (Upper Paths)
Coeurl Pup -> Upper La Noscea (Oakwood)
Antelope Stag -> South Shroud (Silent Arbor)
Balloon -> North Shroud (Alder Springs)
Chasm Buzzard -> Eastern Thanalan (Wellwick Wood)
Axe Beak -> Eastern Thanalan (Wellwick Wood)
Clay Golem -> North Shroud (Alder Springs)
Sandstone Golem -> Southern Thanalan (Broken Water)
Brood Ziz -> Central Shroud (Sorrel Haven)
Lindwurm -> Central Shroud (Sorrel Haven)""",
4: """Qiqirn Gullroaster -> Eastern La Noscea (Bloodshore)
Grass Raptor -> Eastern La Noscea (Raincatcher Gully)
Gigantoad -> Eastern La Noscea (Raincatcher Gully)
Sundrake -> Southern Thanalan (Sagolii Desert)
Colibri -> Eastern La Noscea (Bloodshore)
Coeurl -> Outer La Noscea (The Long Climb)
Mildewed Goobbue -> Eastern La Noscea (Raincatcher Gully)
Snow Wolf Pup -> Coerthas Central Highlands (Dragonhead)
Feral Croc -> Coerthas Central Highlands (Dragonhead)
Dryad -> North Shroud (Proud Creek)
Taurus -> Coerthas Central Highlands (Providence Point)
Molted Ziz -> East Shroud (Larkscall)""",
5: """Quartz Doblyn -> Eastern Thanalan (The Burning Wall)
Lammergeyer -> Western La Noscea (The Isles of Umbra)
3rd Cohort Laquearius -> East Shroud (Larkscall)
Nix -> Mor Dhona (Fogfens)
Mudpuppy -> Mor Dhona (Fogfens)
Wild Hog -> South Shroud (Urth's Gift)
Watchwolf -> North Shroud (Proud Creek)
5th Cohort Laquearius -> Mor Dhona (Fogfens)
Snow Wolf -> Coerthas Central Highlands (Boulder Downs)
Natalan Watchwolf -> Coerthas Central Highlands (Natalan)
Axolotl -> Western La Noscea (Sapsa Spawning Grounds)
Zahar'ak Battle Drake -> Southern Thanalan (Zahar'ak)
4th Cohort Vanguard -> Western Thanalan (Cape Westwind)""",
}

archer = {
1: """Little Ladybug -> North Shroud
Ground Squirrel -> Central Shroud
Forest Funguar -> Central Shroud
Miteling -> North Shroud
Midge Swarm -> North Shroud
Water Sprite -> Central Shroud
Black Eft -> Central Shroud
Anole -> Central Shroud
Trickster Imp -> Central Shroud
Roselet -> Central Shroud""",
2: """Hornet Swarm -> Central Shroud
Arbor Buzzard -> Central Shroud
Magicked Bones -> Central Shroud
Treant Sapling -> Central Shroud
Goblin Hunter -> East Shroud
Mandragora -> East Shroud
Wild Hoglet -> East Shroud
Lemur -> East Shroud
Faerie Funguar -> East Shroud
Giant Gnat -> East Shroud
Raptor Poacher -> East Shroud
Antelope Doe -> South Shroud
Wild Boar -> East Shroud""",
3: """Stoneshell -> Upper La Noscea
Diseased Treant -> East Shroud
Overgrown Offering -> South Shroud
Yarzon Scavenger -> Western Thanalan/North Shroud
Forest Yarzon -> Upper La Noscea
Jumping Djigga -> East Shroud
Redbelly Sharpeye -> South Shroud
Banemite -> North Shroud
Chasm Buzzard -> Eastern Thanalan
Sandskin Peiste -> Southern Thanalan
Ziz -> North Shroud
Toadstool -> Central Shroud
Apkallu -> Eastern La Noscea""",
4: """Floating Eye -> Central Shroud
Sandworm -> Southern Thanalan
Russet Yarzon -> Southern Thanalan
Giant Pelican -> Eastern La Noscea
Smoke Bomb -> Southern Thanalan
Spriggan -> Central Shroud
Bloodshore Bell -> Eastern La Noscea
Jungle Coeurl -> Eastern La Noscea
Ringtail -> Outer La Noscea
Highland Condor -> Outer La Noscea
Salamander -> Upper La Noscea
Fallen Pikeman -> Southern Thanalan
Ice Sprite -> Coerthas Central Highlands
Feral Croc -> Coerthas Central Highlands
Vodoriga -> Coerthas Central Highlands
Baritine Croc -> Coerthas Central Highlands""",
5: """Hippocerf -> Coerthas Central Highlands
Dragonfly -> Coerthas Central Highlands
Oldgrowth Treant -> East Shroud
Lammergeyer -> Western La Noscea
Dead Man's Moan -> Western La Noscea
Morbol -> East Shroud
Mudpuppy -> Mor Dhona
Lesser Kalong -> South Shroud
Giant Reader -> Coerthas Central Highlands
Hippogryph -> Mor Dhona
5th Cohort Secutor -> Mor Dhona
Tempered Gladiator -> Southern Thanalan
Sylphlands Condor -> East Shroud
Milkroot Sapling -> East Shroud
Ahriman -> Northern Thanalan
Shelfeye Reaver -> Western La Noscea""",
}

conjurer = {
1: """Little Ladybug -> Central Shroud
Ground Squirrel -> Central Shroud
Forest Funguar -> Central Shroud
Miteling -> North Shroud
Chigoe -> Central Shroud
Water Sprite -> Central Shroud
Midge Swarm -> North Shroud
Microchu -> North Shroud
Syrphid Swarm -> Central Shroud
Northern Vulture -> East Shroud""",
2: """Tree Slug -> Central Shroud
Arbor Buzzard -> Central Shroud
Goblin Hunter -> East Shroud
Firefly -> Eastern Thanalan, Central Shroud
Mandragora -> East Shroud
Boring Weevil -> East Shroud
Faerie Funguar -> East Shroud
Giant Gnat -> East Shroud
Wolf Poacher -> East Shroud
Qiqirn Beater -> South Shroud
Black Bat -> East Shroud""",
3: """Stoneshell -> Upper La Noscea
Laughing Toad -> Western Thanalan
Diseased Treant -> East Shroud
Lead Coblyn -> Western Thanalan
Bark Eft -> South Shroud
Glowfly -> East Shroud
Antelope Stag -> South Shroud
Sabotender -> Southern Thanalan
Qiqirn Roerunner -> Eastern Thanalan
Goblin Thug -> South Shroud
Toadstool -> Central Shroud
Apkallu -> Eastern La Noscea""",
4: """Lindwurm -> Central Shroud
Gigantoad -> Eastern La Noscea
Bigmouth Orobon -> South Shroud
Mamool Ja Infiltrator -> Upper La Noscea
Sandworm -> Southern Thanalan
Revenant -> Central Shroud
Bloodshore Bell -> Eastern La Noscea
Ornery Karakul -> Coerthas Central Highlands
Deepvoid Deathmouse -> South Shroud
Dryad -> North Shroud
Downy Aevis -> Coerthas Central Highlands
Will-o'-the-wisp -> South Shroud
Dragonfly -> Coerthas Central Highlands""",
5: """Golden Fleece -> Eastern Thanalan
Grenade -> Outer La Noscea
Hippocerf -> Coerthas Central Highlands
Lammergeyer -> Western La Noscea
Dead Man's Moan -> Western La Noscea
3rd Cohort Hoplomachus -> East Shroud
Lesser Kalong -> South Shroud
Snow Wolf -> Coerthas Central Highlands
5th Cohort Eques -> Mor Dhona
Sea Wasp -> Western La Noscea
Sylph Bonnet -> East Shroud
Ahriman -> Northern Thanalan
2nd Cohort Vanguard -> Eastern La Noscea""",
}

gladiator = {
1: """Little Ladybug -> Western Thanalan (The Eighty Sins of Sasamo)
Star Marmot -> Central Thanalan (Spineless Basin)
Cactuar -> Western Thanalan (The Eighty Sins of Sasamo)
Snapping Shrew -> Central Thanalan (Spineless Basin)
Hammer Beak -> Western Thanalan (Hammerlea)
Antling Worker -> Central Thanalan (Black Brush)
Earth Sprite -> Western Thanalan (Hammerlea)
Spriggan Graverobber -> Central Thanalan (Black Brush)
Qiqirn Shellsweeper -> Central Thanalan (Black Brush)
Antling Soldier -> Central Thanalan (The Clutch)
Dusty Mongrel -> Western Thanalan (Horizon's Edge)""",
2: """Bomb -> Western Thanalan (Horizon's Edge)
Copper Coblyn -> Western Thanalan (Horizon's Edge)
Cochineal Cactuar -> Central Thanalan (The Clutch)
Quiveron Guard -> Central Thanalan (The Clutch)
Giant Tortoise -> Western/Central Thanalan (multiple locations)
Thickshell -> Western Thanalan (The Footfalls)
Scaphite -> Western Thanalan (The Footfalls)
Tuco-tuco -> Eastern Thanalan (Drybone)
Myotragus Billy -> Eastern Thanalan (Drybone)
Vandalous Imp -> Eastern Thanalan (Drybone)
Rotting Noble -> Eastern Thanalan (Drybone)
Bloated Bogy -> Western Thanalan (The Footfalls)""",
3: """Stoneshell -> Upper La Noscea (Oakwood)
Kedtrap -> South Shroud (Upper Paths)
Lead Coblyn -> Western Thanalan (The Footfalls)
Overgrown Offering -> South Shroud (Upper Paths)
Coeurl Pup -> Upper La Noscea (Oakwood)
Balloon -> North Shroud (Alder Springs)
Sabotender -> Southern Thanalan (Broken Water)
Qiqirn Roerunner -> Eastern Thanalan (Wellwick Wood)
Goblin Thug -> South Shroud (Silent Arbor)
Coeurlclaw Cutter -> South Shroud (Silent Arbor)
Apkallu -> Eastern La Noscea (Bloodshore)
Pteroc -> Outer La Noscea (The Long Climb)""",
4: """Floating Eye -> Central Shroud (Sorrel Haven)
Mamool Ja Sophist -> Upper La Noscea (Bronze Lake)
Uragnite -> Upper La Noscea (Bronze Lake)
Adamantoise -> South Shroud (Lower Paths)
Sandworm -> Southern Thanalan (Sagolii Desert)
Deathgaze -> Central Shroud (Sorrel Haven)
Velociraptor -> Outer La Noscea (The Long Climb)
Fallen Wizard -> Southern Thanalan (Sagolii Desert)
Snow Wolf Pup -> Coerthas Central Highlands (Dragonhead)
Treant -> South Shroud (Snakemolt)
Vodoriga -> Coerthas Central Highlands (Providence Point)
Hippocerf -> Coerthas Central Highlands (Whitebrim)
Grenade -> Outer La Noscea (Iron Lake)""",
5: """Preying Mantis -> Western La Noscea (The Isles of Umbra)
Lammergeyer -> Western La Noscea (The Isles of Umbra)
Oldgrowth Treant -> East Shroud (Larkscall)
3rd Cohort Eques -> East Shroud (Larkscall)
Dead Man's Moan -> Western La Noscea (The Isles of Umbra)
Morbol -> East Shroud (Larkscall)
Mudpuppy -> Mor Dhona/Coerthas Central Highlands (Fogfens/Boulder Downs)
Lake Cobra -> Mor Dhona (North Silvertear)
Giant Lugger -> Coerthas Central Highlands (Boulder Downs)
Tempered Orator -> Southern Thanalan (Zanr'ak)
Dullahan -> North Shroud (Proud Creek)
Basilisk -> Northern Thanalan (Bluefog)
Gigas Bhikkhu -> Mor Dhona (North Silvertear)
2nd Cohort Hoplomachus -> Eastern La Noscea (Agelyss Wise)""",
}

lancer = {
1: """Little Ladybug -> Central Shroud
Ground Squirrel -> Central Shroud
Forest Funguar -> Central Shroud
Miteling -> North Shroud
Opo-opo -> North Shroud
Microchu -> North Shroud, Central Shroud
Black Eft -> Central Shroud
Bog Yarzon -> Central Shroud
Hoglet -> Central Shroud
Anole -> Central Shroud
Diremite -> Central Shroud
Tree Slug -> East Shroud, Central Shroud""",
2: """Arbor Buzzard -> Central Shroud
Treant Sapling -> Central Shroud
Mandragora -> East Shroud
Wild Hoglet -> East Shroud
Lemur -> East Shroud
Boring Weevil -> East Shroud
Faerie Funguar -> East Shroud
Giant Gnat -> East Shroud
Boar Poacher -> East Shroud
Ziz Gorlin -> East Shroud
Black Bat -> East Shroud
Qiqirn Beater -> South Shroud
Antelope Doe -> South Shroud""",
3: """Stoneshell -> Upper La Noscea
Smallmouth Orobon -> South Shroud
Yarzon Scavenger -> North Shroud, Western Thanalan
Redbelly Lookout -> South Shroud
Antelope Stag -> South Shroud
Moondrip Piledriver -> Western Thanalan
Sabotender -> Southern Thanalan
Goblin Thug -> South Shroud
Sandskin Peiste -> Southern Thanalan
Corpse Brigade Firedancer -> Southern Thanalan
Coeurlclaw Poacher -> South Shroud
Apkallu -> Eastern La Noscea
Midland Condor -> South Shroud""",
4: """Floating Eye -> Central Shroud
Large Buffalo -> Eastern La Noscea
Smoke Bomb -> Southern Thanalan
Sundrake -> Southern Thanalan
Spriggan -> Central Shroud
Basalt Golem -> Outer La Noscea
Ringtail -> Outer La Noscea
Ornery Karakul -> Coerthas Central Highlands
Lesser Kalong -> North Shroud
Snow Wolf Pup -> Coerthas Central Highlands
Dryad -> North Shroud
Bateleur -> Coerthas Central Highlands
Downy Aevis -> Coerthas Central Highlands
Mirrorknight -> Eastern Thanalan""",
5: """Dragonfly -> Coerthas Central Highlands
Baritine Croc -> Coerthas Central Highlands
Dead Man's Moan -> Western La Noscea
3rd Cohort Signifer -> East Shroud
Morbol -> East Shroud
Wild Hog -> South Shroud
Daring Harrier -> Mor Dhona
Lake Cobra -> Mor Dhona
Snow Wolf -> Coerthas Central Highlands
Sea Wasp -> Western La Noscea
5th Cohort Vanguard -> Mor Dhona
Natalan Watchwolf -> Coerthas Central Highlands
Sylphlands Sentinel -> East Shroud
Basilisk -> Northern Thanalan
2nd Cohort Eques -> Eastern La Noscea""",
}

marauder = {
1: """Little Ladybug -> Middle La Noscea (Zephyr Drift)
Wharf Rat -> Middle La Noscea (Zephyr Drift)
Aurelia -> Lower La Noscea (Moraby Bay)
Bee Cloud -> Middle La Noscea (Summerford)
Wild Dodo -> Lower La Noscea (Cedarwood)
Tiny Mandragora -> Middle La Noscea (Summerford)
Bogy -> Middle La Noscea (Summerford)
Wounded Aurochs -> Middle La Noscea (Summerford)
Grounded Raider -> Middle La Noscea (Summerford)
Megalocrab -> Middle La Noscea (Three-malm Bend)""",
2: """Firefly -> Lower La Noscea
Mossless Goobbue -> Lower La Noscea
Fat Dodo -> Western La Noscea
Moraby Mole -> Lower La Noscea
Qiqirn Eggdigger -> Lower La Noscea
Rhotano Buccaneer -> Western La Noscea
Dusk Bat -> Western La Noscea
Puk Hatchling -> Western La Noscea
Hedgemole -> Western La Noscea
Rothlyt Pelican -> Western La Noscea
Killer Mantis -> Western La Noscea
Wild Wolf -> Upper La Noscea""",
3: """Stoneshell -> Upper La Noscea
Diseased Treant -> East Shroud
Yarzon Scavenger -> Western Thanalan
Yarzon Scavenger -> North Shroud
Redbelly Larcener -> South Shroud
Shroud Hare -> North Shroud
Sabotender -> Southern Thanalan
Balloon -> North Shroud
Phurble -> Eastern Thanalan
Sandskin Peiste -> Southern Thanalan
Axe Beak -> Eastern Thanalan
Toadstool -> Central Shroud
Floating Eye -> Central Shroud""",
4: """Stroper -> South Shroud
Stroper -> Central Shroud
Adamantoise -> South Shroud
Smoke Bomb -> Southern Thanalan
Grass Raptor -> Eastern La Noscea
Snipper -> Eastern La Noscea
Bloodshore Bell -> Eastern La Noscea
Jungle Coeurl -> Eastern La Noscea
Snow Wolf Pup -> Coerthas Central Highlands
Redhorn Ogre -> Coerthas Central Highlands
Ornery Karakul -> Coerthas Central Highlands
Highland Goobbue -> Coerthas Central Highlands
Downy Aevis -> Coerthas Central Highlands
Snowstorm Goobbue -> Coerthas Central Highlands
Grenade -> Outer La Noscea""",
5: """Molted Ziz -> East Shroud (Larkscall)
Quartz Doblyn -> Eastern Thanalan (The Burning Wall)
Dead Man's Moan -> Western La Noscea (The Isles of Umbra)
Morbol -> East Shroud (Larkscall)
Crater Golem -> Central Shroud (The Standing Corses)
Wild Hog -> South Shroud (Urth's Gift)
Biast -> Coerthas Central Highlands (Boulder Downs)
5th Cohort Signifer -> Mor Dhona (Fogfens)
Synthetic Doblyn -> Outer La Noscea (U'Ghamaro Mines)
Watchwolf -> North Shroud (Proud Creek)
Iron Tortoise -> Southern Thanalan (Zanr'ak)
Milkroot Cluster -> East Shroud (Sylphlands)
4th Cohort Secutor -> Western Thanalan (Cape Westwind)
2nd Cohort Laquearius -> Eastern La Noscea (Agelyss Wise)""",
}

pugilist = {
1: """Huge Hornet -> Central Thanalan
Star Marmot -> Central Thanalan
Cactuar -> Western Thanalan
Snapping Shrew -> Central Thanalan
Orobon -> Central Thanalan
Nesting Buzzard -> Western Thanalan
Spriggan Graverobber -> Central Thanalan
Goblin Mugger -> Western Thanalan
Sandtoad -> Western Thanalan
Eft -> Central Thanalan
Sun Midge Swarm -> Western Thanalan
Desert Peiste -> Western Thanalan""",
2: """Bomb -> Western Thanalan
Cochineal Cactuar -> Central Thanalan
Antling Sentry -> Central Thanalan
Giant Tortoise -> Western Thanalan
Arbor Buzzard -> Western Thanalan
Scaphite -> Western Thanalan
Thickshell -> Western Thanalan
Tuco-tuco -> Eastern Thanalan
Myotragus Nanny -> Eastern Thanalan
Blowfly Swarm -> Eastern Thanalan
Vandalous Imp -> Eastern Thanalan
Bloated Bogy -> Western Thanalan
Rotting Corpse -> Eastern Thanalan
Rotting Noble -> Eastern Thanalan""",
3: """Overgrown Ivy -> East Shroud
Smallmouth Orobon -> South Shroud
Forest Yarzon -> Upper La Noscea
Coeurl Pup -> Upper La Noscea
Shroud Hare -> North Shroud
Bark Eft -> South Shroud
Fallen Mage -> Southern Thanalan
Ziz -> North Shroud
Corpse Brigade Knuckledancer -> Southern Thanalan
Clay Golem -> North Shroud
Coeurlclaw Hunter -> South Shroud
Lindwurm -> Central Shroud
Bigmouth Orobon -> South Shroud
Apkallu -> Eastern La Noscea""",
4: """Mamool Ja Breeder -> Upper La Noscea
Russet Yarzon -> Southern Thanalan
Smoke Bomb -> Southern Thanalan
Deathgaze -> Central Shroud
Jungle Coeurl -> Eastern La Noscea
Goobbue -> Eastern La Noscea
Basalt Golem -> Outer La Noscea
Velociraptor -> Outer La Noscea
Highland Goobbue -> Coerthas Central Highlands
Feral Croc -> Coerthas Central Highlands
Redhorn Ogre -> Coerthas Central Highlands
Ochu -> East Shroud
Molted Ziz -> East Shroud
Snowstorm Goobbue -> Coerthas Central Highlands""",
5: """Quartz Doblyn -> Eastern Thanalan
Dead Man's Moan -> Western La Noscea (The Isles of Umbra)
3rd Cohort Signifer -> East Shroud
Wild Hog -> South Shroud
Raging Harrier -> Mor Dhona
Biast -> Coerthas Central Highlands
Gigas Shramana -> Mor Dhona
Snow Wolf -> Coerthas Central Highlands
5th Cohort Hoplomachus -> Mor Dhona (Fogfens)
Dreamtoad -> East Shroud
Hapalit -> Mor Dhona
Zahar'ak Battle Drake -> Southern Thanalan
Basilisk -> Northern Thanalan
Shelfclaw Reaver -> Western La Noscea""",
}

rogue = {
1: """Wharf Rat -> Middle La Noscea
Lost Lamb -> Middle La Noscea (Zephyr Drift)
Aurelia -> Lower La Noscea
Wild Dodo -> Lower La Noscea
Pugil -> Middle La Noscea (Summerford)
Goblin Fisher -> Middle La Noscea (Summerford)
Tiny Mandragora -> Middle La Noscea / Lower La Noscea (Cedarwood)
Cave Bat -> Lower La Noscea (Cedarwood)
Galago -> Lower La Noscea (Cedarwood)
Grounded Pirate -> Middle La Noscea (Summerford)
Grounded Raider -> Middle La Noscea (Summerford)
Megalocrab -> Middle La Noscea""",
2: """Wild Jackal -> Lower La Noscea
Roseling -> Western La Noscea (Quarterstone)
Sewer Mole -> Western La Noscea (Quarterstone)
Fat Dodo -> Western La Noscea
Moraby Mole -> Lower La Noscea
Qiqirn Eggdigger -> Lower La Noscea
Puk Hatchling -> Western La Noscea (Skull Valley)
Rothlyt Pelican -> Western La Noscea
Killer Mantis -> Western La Noscea
Hedgemole -> Western La Noscea
Wild Wolf -> Upper La Noscea
Bumble Beetle -> Upper La Noscea (Poor Maid's Mill)""",
3: """Black Bat -> East Shroud
Gall Gnat -> East Shroud
Overgrown Ivy -> East Shroud
Bark Eft -> South Shroud
Redbelly Lookout -> South Shroud
Redbelly Larcener -> South Shroud
Antelope Stag -> South Shroud
River Yarzon -> South Shroud
Corpse Brigade Knuckledancer -> Southern Thanalan
Corpse Brigade Firedancer -> Southern Thanalan
Coeurlclaw Hunter -> South Shroud
Coeurlclaw Cutter -> South Shroud
Sandstone Golem -> Southern Thanalan""",
4: """Large Buffalo -> Eastern La Noscea
Grass Raptor -> Eastern La Noscea
Qiqirn Gullroaster -> Eastern La Noscea
Colibri -> Eastern La Noscea
Coeurl -> Outer La Noscea
Highland Condor -> Outer La Noscea
Basalt Golem -> Outer La Noscea
Velociraptor -> Outer La Noscea
Feral Croc -> Coerthas Central Highlands
Highland Goobbue -> Coerthas Central Highlands
Redhorn Ogre -> Coerthas Central Highlands
Taurus -> Coerthas Central Highlands
Bateleur -> Coerthas Central Highlands
Chinchilla -> Coerthas Central Highlands""",
5: """Golden Fleece -> Eastern Thanalan
Quartz Doblyn -> Eastern Thanalan
Nix -> Mor Dhona
Mudpuppy -> Mor Dhona / Coerthas Central Highlands
Daring Harrier -> Mor Dhona
Raging Harrier -> Mor Dhona
Gigas Shramana -> Mor Dhona
Gigas Sozu -> Mor Dhona
Hippogryph -> Mor Dhona
Hapalit -> Mor Dhona
2nd Cohort Eques -> Eastern La Noscea
2nd Cohort Signifer -> Eastern La Noscea
2nd Cohort Secutor -> Eastern La Noscea
2nd Cohort Vanguard -> Eastern La Noscea""",
}

thaumaturge = {
1: """Little Ladybug -> Western Thanalan
Huge Hornet -> Central Thanalan
Cactuar -> Western Thanalan
Snapping Shrew -> Central Thanalan
Syrphid Cloud -> Central Thanalan
Yarzon Feeder -> Western Thanalan
Rusty Coblyn -> Western Thanalan
Spriggan Graverobber -> Central Thanalan
Qiqirn Shellsweeper -> Central Thanalan
Sun Bat -> Central Thanalan""",
2: """Copper Coblyn -> Western Thanalan
Bomb -> Western Thanalan
Cochineal Cactuar -> Central Thanalan
Quiveron Attendant -> Central Thanalan
Giant Tortoise -> Western Thanalan
Antling Sentry -> Central Thanalan
Thickshell -> Western Thanalan
Toxic Toad -> Central Thanalan
Tuco-tuco -> Eastern Thanalan
Myotragus Nanny -> Eastern Thanalan
Blowfly Swarm -> Eastern Thanalan
Rotting Corpse -> Eastern Thanalan
Bloated Bogy -> Western Thanalan""",
3: """Kedtrap -> South Shroud (Upper Paths)
Overgrown Ivy -> East Shroud (Nine Ivies)
Yarzon Scavenger -> Western Thanalan (Cape Westwind)
Forest Yarzon -> Upper La Noscea (Oakwood)
Laughing Toad -> Western Thanalan (The Footfalls)
Bark Eft -> South Shroud (Upper Paths)
Jumping Djigga -> East Shroud (The Bramble Patch)
Glowfly -> East Shroud (The Bramble Patch)
River Yarzon -> South Shroud (Silent Arbor)
Potter Wasp Swarm -> Southern Thanalan
Phurble -> Eastern Thanalan (Wellwick Wood)
Corpse Brigade Knuckledancer -> Southern Thanalan (Broken Water)
Fire Sprite -> Southern Thanalan (The Red Labyrinth)
Stroper -> Central Shroud (Sorrel Haven)""",
4: """Adamantoise -> South Shroud
Mamool Ja Executioner -> Upper La Noscea
Revenant -> Central Shroud
Russet Yarzon -> Southern Thanalan
Smoke Bomb -> Southern Thanalan
Dung Midge Swarm -> Eastern La Noscea
Gigantoad -> Eastern La Noscea
Spriggan -> Central Shroud
Salamander -> Upper La Noscea
Plasmoid -> Outer La Noscea
Ice Sprite -> Coerthas Central Highlands
Feral Croc -> Coerthas Central Highlands
Will-o'-the-wisp -> South Shroud
Golden Fleece -> Eastern Thanalan""",
5: """Oldgrowth Treant -> East Shroud
Dragonfly -> Coerthas Central Highlands
Crater Golem -> Central Shroud
Dead Man's Moan -> Western La Noscea
3rd Cohort Secutor -> East Shroud
Morbol -> East Shroud
Nix -> Mor Dhona
Lesser Kalong -> South Shroud
Gigas Sozu -> Mor Dhona
Giant Logger -> Coerthas Central Highlands
Iron Tortoise -> Southern Thanalan
Synthetic Doblyn -> Outer La Noscea
Ked -> South Shroud
4th Cohort Hoplomachus -> Western Thanalan
2nd Cohort Signifer -> Eastern La Noscea""",
}

maelstrom = {
    1: """Amalj'aa Hunter -> Eastern Thanalan (Sandgate)
Heckler Imp -> Halatali
Doctore -> Halatali
Firemane -> Halatali
Sylvan Groan -> East Shroud (The Bramble Patch)
Sylvan Sough -> East Shroud (The Bramble Patch)
Kobold Pickman -> Upper La Noscea (Oakwood)
Amalj'aa Bruiser -> Southern Thanalan (Broken Water)
Ixali Straightbeak -> North Shroud (Alder Springs)
Ixali Wildtalon -> Coerthas Central Highlands""",
    2: """Amalj'aa Divinator -> Southern Thanalan (Sagolii Desert)
Kobold Pitman -> Eastern La Noscea (Bloodshore)
Temple Bat -> The Sunken Temple of Qarn
The Condemned -> The Sunken Temple of Qarn
Teratotaur -> The Sunken Temple of Qarn
Kobold Bedesman -> Outer La Noscea (Iron Lake)
Kobold Priest -> Outer La Noscea (Iron Lake)
Sylvan Sigh -> East Shroud (Larkscall)
Shelfscale Sahagin -> Western La Noscea (Halfstone)
Amalj'aa Pugilist -> Southern Thanalan (Zanr'ak)""",
    3: """Ixali Boldwing -> North Shroud (Proud Creek)
Sylpheed Screech -> East Shroud (Sylphlands)
U'Ghamaro Bedesman -> Outer La Noscea (U'Ghamaro Mines)
Trenchtooth Sahagin -> Western La Noscea (Halfstone)
Sapsa Shelfclaw -> Western La Noscea (Sapsa Spawning Grounds)
Zahar'ak Archer -> Southern Thanalan (Zahar'ak)
Natalan Fogcaller -> Coerthas Central Highlands (Natalan)
Natalan Boldwing -> Coerthas Central Highlands (Natalan)
Tonberry -> The Wanderer's Palace
Giant Bavarois -> The Wanderer's Palace""",
}

order_of_the_twin_adder = {
    1: """Amalj'aa Javelinier -> Eastern Thanalan (Sandgate)
Heckler Imp -> Halatali
Scythe Mantis -> Halatali
Coliseum Python -> Halatali
Sylvan Scream -> East Shroud (The Bramble Patch)
Kobold Pickman -> Upper La Noscea (Oakwood)
Amalj'aa Bruiser -> Southern Thanalan / Eastern Thanalan
Amalj'aa Ranger -> Eastern Thanalan (Wellwick Wood)
Ixali Deftalon -> North Shroud (Alder Springs)
Ixali Fearcaller -> Coerthas Central Highlands (Dragonhead)""",
    2: """Amalj'aa Sniper -> Southern Thanalan (Sagolii Desert)
Kobold Missionary -> Eastern La Noscea (Bloodshore)
Kobold Sidesman -> Upper La Noscea (Zelma's Run)
Temple Bee -> The Sunken Temple of Qarn
Temple Guardian -> The Sunken Temple of Qarn
Kobold Roundsman -> Outer La Noscea (Iron Lake)
Sylvan Snarl -> East Shroud (Larkscall)
Shelfclaw Sahagin -> Western La Noscea (Halfstone)
Amalj'aa Lancer -> Southern Thanalan (Zanr'ak)
U'Ghamaro Roundsman -> Outer La Noscea (U'Ghamaro Mines)""",
    3: """Ixali Windtalon -> North Shroud (Proud Creek)
Sylpheed Snarl -> East Shroud (Sylphlands)
U'Ghamaro Quarryman -> Outer La Noscea (U'Ghamaro Mines)
Sapsa Shelftooth -> Western La Noscea (Sapsa Spawning Grounds)
Zahar'ak Pugilist -> Southern Thanalan
Natalan Swiftbeak -> Coerthas Central Highlands
Natalan Boldwing -> Coerthas Central Highlands
Tonberry -> The Wanderer's Palace
Bronze Beetle -> The Wanderer's Palace
Keeper of Halidom -> The Wanderer's Palace""",
}

immortal_flames = {
    1: """Amalj'aa Hunter -> Eastern Thanalan (Sandgate)
Doctore -> Halatali
Firemane -> Halatali
Thunderclap Guivre -> Halatali
Sylvan Sough -> East Shroud (The Bramble Patch)
Kobold Footman -> Upper La Noscea (Oakwood)
Kobold Pickman -> Upper La Noscea (Oakwood)
Amalj'aa Seer -> Southern Thanalan (Broken Water)
Ixali Lightwing -> North Shroud (Alder Springs)
Ixali Boundwing -> Coerthas Central Highlands""",
    2: """Amalj'aa Halberdier -> Southern Thanalan (Sagolii Desert)
Kobold Missionary -> Eastern La Noscea (Bloodshore)
Kobold Sidesman -> Upper La Noscea (Zelma's Run)
Sand Bat -> Cutter's Cry
Sabotender Desertor -> Cutter's Cry
Myrmidon Princess -> Cutter's Cry
Kobold Quarryman -> Outer La Noscea (Iron Lake)
Sylvan Screech -> East Shroud (Larkscall)
Shelfspine Sahagin -> Western La Noscea (Halfstone)
Amalj'aa Archer -> Southern Thanalan (Zanr'ak)""",
    3: """Ixali Windtalon -> North Shroud (Proud Creek)
Sylpheed Sigh -> East Shroud
U'Ghamaro Priest -> Outer La Noscea (U'Ghamaro Mines)
Sapsa Shelfspine -> Western La Noscea (Sapsa Spawning Grounds)
Zahar'ak Thaumaturge -> Southern Thanalan (Zahar'ak)
Natalan Windtalon -> Coerthas Central Highlands (Natalan)
Natalan Boldwing -> Coerthas Central Highlands (Natalan)
Tonberry -> The Wanderer's Palace
Corrupted Nymian -> The Wanderer's Palace
Soldier of Nym -> The Wanderer's Palace""",
}

ALL = {
    "Arcanist": (arcanist, "->"),
    "Archer": (archer, "->"),
    "Conjurer": (conjurer, "->"),
    "Gladiator": (gladiator, "->"),
    "Lancer": (lancer, "->"),
    "Marauder": (marauder, "->"),
    "Pugilist": (pugilist, "->"),
    "Rogue": (rogue, "->"),
    "Thaumaturge": (thaumaturge, "->"),
    "Maelstrom": (maelstrom, "->"),
    "Order of the Twin Adder": (order_of_the_twin_adder, "->"),
    "Immortal Flames": (immortal_flames, "->"),
}

rows = []
paren_re = re.compile(r"^(.*?)\s*\(([^)]+)\)\s*$")

for cls, (ranks, sep) in ALL.items():
    for rank, block in ranks.items():
        for line in block.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            if sep == "-":
                # single-hyphen separator, careful not to split on hyphenated
                # names; split on " - " only
                monster, loczone = line.split(" - ", 1)
            else:
                monster, loczone = line.split(sep, 1)
            monster = monster.strip()
            loczone = loczone.strip()
            m = paren_re.match(loczone)
            if m:
                zone, area = m.group(1).strip(), m.group(2).strip()
            else:
                zone, area = loczone, ""
            rows.append({
                "class": cls,
                "rank": rank,
                "monster": monster,
                "zone": zone,
                "area": area,
            })

split_re = re.compile(r"\s*/\s*|\s*,\s*")
SUFFIXES = ["Thanalan", "La Noscea", "Shroud", "Highlands"]
DIRECTION_WORDS = {
    "Central", "Western", "Eastern", "Southern", "Northern",
    "Outer", "Upper", "Lower",
}


def expand_zone(zone_str):
    parts = [p.strip() for p in split_re.split(zone_str) if p.strip()]
    for i in range(len(parts) - 2, -1, -1):
        if parts[i] in DIRECTION_WORDS:
            nxt = parts[i + 1]
            for suf in SUFFIXES:
                if suf in nxt:
                    parts[i] = parts[i] + " " + suf
                    break
    return parts


final_rows = []
for r in rows:
    zones = expand_zone(r["zone"])
    single = len(zones) == 1
    for z in zones:
        final_rows.append({
            "class": r["class"],
            "rank": r["rank"],
            "monster": r["monster"],
            "zone": z,
            "area": r["area"] if single else "",
        })

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_JSON, "w") as f:
    json.dump(final_rows, f, indent=1)

print(f"wrote {OUT_JSON}")
print(f"Total rows (pre-split): {len(rows)}")
print(f"Total rows (post-split): {len(final_rows)}")
zones = sorted(set(r["zone"] for r in final_rows))
print(f"Distinct zones: {len(zones)}")
for z in zones:
    print(" -", z)

# Premise / Guiding thoughts

It's fun to have decks of cards
 * It's fun to build a deck
 * It's fun to collect certain cards

Having rules on cards in front of you is better than having rules in a book
 * It takes more time to find the page with a particular rule

Arithmetic sucks.  Stop doing it.
 * "Flip 3, take the best" is way easier than roll 2d6, add your Strength bonus

Cards open up richer game play (unpredictable might be substituted for "random")
 * Dice:
  - carrying more than 10 is cumbersome
  - roll one to get a linear, bounded random value
  - roll multiple to get different distributions of random values
  - use a die as a marker
  - use a die & it's shown pip value as an enumerated marker
  - roll a die and hide its value for other players to guess
  - collect special dice
 * Cards:
  - carrying more than 200 is cumbersome
  - flip a card to get a bounded random value in whatever distribution the deck has
  - flip one to get multi-dimensional random values (eg, suit & number & face)
  - flip, without replacement, a series of cards from a deck with a ~known distribution
   - (deckbuilding mechanic)
  - flip a card and hide its value for other players to guess
  - collect special cards
   - collect cards that are normal in one dimension, but special in another
  - build a deck of cards (with dice this is possible, but cumbersome)
  - cards can be written on
  - cards can be drafted
  - player choice about when to shuffle can be interesting
  - the shuffle itself can be interesting
   - cut the deck
   - put a single card in the middle / at the bottom / on the top
   - look at top x cards, and put them back in any order
  - the backs can be
   - identical - to mask what the result will be
   - marked - to hint or make obvious what the result will be

## Example conversations I want to prevent:

>>> DM: Ok, so roll to see if you hit
>>> P1: I got a 14.
>>> DM: Is that before modifiers?
>>> P1: Oh right, I've got a dex bonus, so that's 14 plus 1
>>> DM: Ok, so you got a 15...
>>> P2: Dude, your bow is magic too!
>>> P1: Oh right!  So yeah, that's a plus 2
>>> DM: You mean your total modifier is plus 2, or just your bow?
>>> P1: No, bow is plus 1
>>> DM: So what'd you get?
>>> P1: I got a... 16!

So what is this getting at?  I guess the main thing is the player
knows what to do *before* they flip and everyont can immediately interpret
their result when seeing the flip.

----

# Character:

Trainable Attributes: (scores: red, yellow, green, blue)
 * Strength (muscles, endurance, constitution)
 * Dexterity (aim, catching, evasion)
 * Intelligence (charm, figuring, creation)

Other ideas...
 * Movement: Strength + Encumberance + Tiredness
 * Personality: ??? Maybe the DM decides to throw in red or green cards based on personality

Jason Bourne (4s in all categories) is possible, but throw in some other weakness / vulnerability to make the story good.

### Common skills:

  Something that you have a clear idea how it works - climbing, ducking, lying, arguing, swimming

### Proficiency:

"Classes" and "levels" of other RPGs seem very synthetic.
Brains learn, muscles learn, the nervous system learns.  People can step out of
their comfort zones.  People can try something new.  We know we're going to fail at first, and as adults,
a fear of failure usually holds us back.  It's practice that makes us proficient.

The game should let characters try anything reasonable, fail a lot, and through practice, get better.

Attempting skills and building up proficiency:

 * Grab a blank card, write the skill on a card, put 2 or 3 (see below) red cards on top.
 * Decide which attribute governs it.

To use the skill:

 * Flip 1 + (# of red cards).  Take lowest score.
 * Note: taking lowest score can mean that without a blessing, it is IMPOSSIBLE to get 2 ✔✔
 * If *x* card has a proficiency symbol on it, discard one of the red cards.
  * any of the flipped cards?
   * this might be best. makes digging out of the hole go faster
   * that learning curve shape is `-3: 70%, -2: 60%, -1: 45%, 0: 25%`
   * but only allow one proficiency gain even if there are multiple proficiency symbols, otherwise they could jump from -2 to +1 and that doesn't make much sense.
  * only the card that got used?
   * that learning curve shape is different depending on the suit:
    * `-3: 16%, -2: 19%, -1: 22%, 0: 25%` for Anchor
    * `-3: 9%, -2: 12%, -1: 17%, 0: 25%` for Bulb
    * `-3: 24%, -2: 23%, -1: 25%, 0: 25%` for Crescent
    * `-3: 11%, -2: 14%, -1: 18%, 0: 25%` for Dart
    * This seems super wonky.  Maybe it can be adjusted if I want to pursue it.
    * Ok, I've edited the cards, they would now give this learning curve:
    * `-3: 24%, -2: 25%, -1: 26%, 0: 25%` for Anchor
    * `-3: 27%, -2: 29%, -1: 28%, 0: 25%` for Bulb
    * `-3: 33%, -2: 28%, -1: 25%, 0: 25%` for Crescent
    * `-3: 36%, -2: 32%, -1: 29%, 0: 25%` for Dart
  * or work into each skill "family" some kind of learning curve.
 * etc
 * If you flip a proficiency symbol when there are no red cards remaining, add a green card on top of the skill card.
 * From now on, flip 1 + (# of green cards) and take the highest score
 * If you flip *2* proficiency symbols when there's one green card, add *another* green card.
  * this means the learning curve ends with a `1: 5%`. ie, a 1/20 probability of graduating to +2
   * `(5.0/20) * (4.0/19) = 0.526`
 * Proficiency maxes out at 2 green cards

New skills:
 * Something you've never seen anyone do before - new spell, bird call, snatch an arrow, swimming, even some magic
 * If you spend time merely watching carefully (and without distractions) when someone succeeds in a skill, you can start it out with 3 red cards on top
 * If someone spends time teaching you the basics, you can start it out with 2 red cards on top
 * *Idea:* DM can choose to put a **personality-block-card** on a skill in critical or repeated failures
  * Your character fucks up so bad, that they think there's something wrong with them.  Anxiety, Frustration, etc.

### Analysis

```
# -3: Without any instruction or related skills, the character tries something new
>>> analyze_check(a, -3)
({False: 9840, True: 160}, '1.6% / 98.4%') # They're weak in that attribute so it's nearly impossible.

>>> analyze_check(b, -3)
({False: 9739, True: 261}, '2.6% / 97.4%')

>>> analyze_check(c, -3)
({False: 9334, True: 666}, '6.7% / 93.3%') # They're strong in that attribute so there's hope.

>>> analyze_check(d, -3)
({False: 9027, True: 973}, '9.7% / 90.3%')


# -2: A character is introduced to a new skill with some instruction

>>> analyze_check(a, -2)
({False: 9514, True: 486}, '4.9% / 95.1%') # They're weak, so there's a 1/20 chance.

>>> analyze_check(b, -2)
({False: 9264, True: 736}, '7.4% / 92.6%')

>>> analyze_check(c, -2)
({False: 8537, True: 1463}, '14.6% / 85.4%') # They're strong, so there's a 3/20 chance.

>>> analyze_check(d, -2)
({False: 8033, True: 1967}, '19.7% / 80.3%')

```

 New equipment they haven't used works the same way
  - except if they've used that "class" of equipment before, then they start with one red card (or one fewer green cards)
  - *except* if it's a clone.  One AK-47 is the same as any other.


Skills can be copied from D&D & Pathfinder
http://paizo.com/pathfinderRPG/prd/coreRulebook/feats.html

It makes sense that some stuff should come before other stuff.  Jogging 5 blocks comes before running a marathon.
Drawing in black & white comes before oils, so **skill trees** kind of make sense.

 * Maybe if you have the drawing skill at +1, you can attempt the painting skill starting at -1, instead of -2.
 * Maybe a "related skill symbol" on the cards, like the corner symbols in 7 Wonders

*Idea:* during camp-out phase, they can choose only one skill and make one attempt per camp to up a skill. (By flipping and getting a proficiency card).  during level-up phase (resting near resources where they can reasonably learn the skill), they get 3 attempts that they can devote to one skill, or split up among many skills.

### New Analysis

```
In [2]: cards.analyze_green_token_check()
70144/200000 (35.1%) Rank a, Mod -2, Stamina loss: 0
59076/200000 (29.5%) Rank a, Mod -1, Stamina loss: 0
49771/200000 (24.9%) Rank a, Mod 0, Stamina loss: 0
63295/200000 (31.6%) Rank a, Mod 1, Stamina loss: 0

98564/200000 (49.3%) Rank b, Mod -2, Stamina loss: 0
80165/200000 (40.1%) Rank b, Mod -1, Stamina loss: 0
49959/200000 (25.0%) Rank b, Mod 0, Stamina loss: 0
36041/200000 (18.0%) Rank b, Mod 1, Stamina loss: 0

100295/200000 (50.1%) Rank c, Mod -2, Stamina loss: 0
76970/200000 (38.5%) Rank c, Mod -1, Stamina loss: 0
49832/200000 (24.9%) Rank c, Mod 0, Stamina loss: 0
35042/200000 (17.5%) Rank c, Mod 1, Stamina loss: 0

96896/200000 (48.4%) Rank d, Mod -2, Stamina loss: 0
77988/200000 (39.0%) Rank d, Mod -1, Stamina loss: 0
50143/200000 (25.1%) Rank d, Mod 0, Stamina loss: 0
40191/200000 (20.1%) Rank d, Mod 1, Stamina loss: 0

69312/200000 (34.7%) Rank a, Mod -2, Stamina loss: 8
56541/200000 (28.3%) Rank a, Mod -1, Stamina loss: 8
43576/200000 (21.8%) Rank a, Mod 0, Stamina loss: 8
55472/200000 (27.7%) Rank a, Mod 1, Stamina loss: 8

81539/200000 (40.8%) Rank b, Mod -2, Stamina loss: 8
66938/200000 (33.5%) Rank b, Mod -1, Stamina loss: 8
43158/200000 (21.6%) Rank b, Mod 0, Stamina loss: 8
43086/200000 (21.5%) Rank b, Mod 1, Stamina loss: 8

72629/200000 (36.3%) Rank c, Mod -2, Stamina loss: 8
52983/200000 (26.5%) Rank c, Mod -1, Stamina loss: 8
43406/200000 (21.7%) Rank c, Mod 0, Stamina loss: 8
42499/200000 (21.2%) Rank c, Mod 1, Stamina loss: 8

93714/200000 (46.9%) Rank d, Mod -2, Stamina loss: 8
71802/200000 (35.9%) Rank d, Mod -1, Stamina loss: 8
43600/200000 (21.8%) Rank d, Mod 0, Stamina loss: 8
28788/200000 (14.4%) Rank d, Mod 1, Stamina loss: 8
```

 suit    | -2  | -1  | 0   | 1   |
---------|-----|-----|-----|-----|
Anchor   | 35% | 30% | 25% | 32% |
Bulb     | 49% | 40% | 25% | 18% |
Crescent | 50% | 39% | 25% | 18% |
Dart     | 48% | 39% | 25% | 20% |

After losing 8 Stamina:

 suit    | -2  | -1  | 0   | 1   |
---------|-----|-----|-----|-----|
Anchor   | 35% | 28% | 22% | 28% |
Bulb     | 41% | 34% | 22% | 22% |
Crescent | 36% | 27% | 22% | 21% |
Dart     | 47% | 36% | 22% | 14% |


## Challenges

 * Classes and levels are tools to manage the balance of the game.  Players might be able to unbalance the play experience
 * Especially if the players & GM can just decide on a new skill name, write it on a card and say "Here ya go"
 * The GM **must** understand that there are situations where a character doesn't have certain possibilities available to them.
  * Rolling a d20 can *always* get you a critical success or critical failure
  * Resolution cards can get you into situations where you never will
   * eg, no crit successes while: -2 penalty in Anchor, tired in Anchor, -1 and tired in Bulb, etc.

 * Players that lose focus of the story and only grind their skills up to the highest levels
  * GM can deal a red card or red token on that skill to mark that the character is "frustrated" and is now trying in vain
  * Or the GM could add some narrative flavour about how that character has developed some other emotional relationship
    with that skill and is thus blocked, and perhaps even penalized
    * The GM could do this conditionally on the character getting ✗s.
    * Anxiety / frustration / embarassment
  * Or, the player could start with 1 green card any time they're fully rested
   * They can't normally exceed that 1 green card - resting extra doesn't earn them 2 cards
   * When they flip a proficiency symbol, they can *choose* to take the card into the skill they just used

----
# Thematic flips:

### A Chase / Running away
   * both characters can choose color direction up to their dexterity
   * runner gets a 1-card head start - looks at top card, decides which color to flip
   * runner flips up 2 green - chaser must exactly match the sum, so 3 green
   * chaser flips 1 green.  sum: 2 green
   * runner flips 1 green.  sum: 3 green
   * chaser flips 2 green. sum: 1 green
     some possibilities from here:
       - runner flips 1 red.  sum 0.  Runner is caught (runner hits dead end or trips)
       - runner flips 2 red. sum -1 (runner zigs the other way, still running.  chaser now needs 1 red)
   * if decks run out, runner has escaped
   * if runner gets a 5 point delta, runner has escaped

   - Chase doesn't have to be just for footraces.  Imagine if they're making a case to the town mayor, against the counter-arguments of an adversary.

### Silent Communication:
 * both characters silently pick up & look at the top card of their flip decks
 * they can then say exactly one word - the color they're going to flip (they can say it in any turn order, or DM can decide)
 * they then flip that color - if the points match, they succeed.


### Bluffing or deciding on gear could work like liar's dice
 - draw 5 of your cards, so does the opponent(s)
 - go around and say how many ✔s the whole group can make
 - eventually someone calls out the previous person
 - all cards are shown
 - if the callee has an attribute advantage, they can add that many extra cards (from the top of their deck)
 - but I have to make sure the distribution of ✗'s and ✔'s is even for that game.


### Dividing up treasure:

This works if there are more treasure cards than the number of players
 * shuffle the treasure cards
 * deal equal decks to each player
  * if decks are unequal, do a flip and the players with the highest get the decks with the extra cards
 * player takes one card, then passes the deck to the player to the left.
 * repeat until empty
You could add in a stealth skill check part here, and they have to show cards face up unless they pass the stealth check.


### Blessing cards:
 * 2 green on all sides
 * color cards that go in the flip deck
 * awarded by the DM - maybe for roleplaying or for other epicness
 * they have 1 or 2 proficiency markers
 * once they come up & take their effect, they go back to the DM
   - similarly, lucky rings / amulets do the same thing, but when they come up they go under the character's ring/amulet card until appropriate to shuffle them back in

 Curse cards:
  * work similarly, awarded for similar reasons

### Combat:
      A series of X vs Y flips
      Landing blows can bruise, tire, wound, subdue, kill.

    Tire: (bruising can be the same but only for physical and you can't shake it off)
    - lvl 1: can't go to blue
    - lvl 2-4: get a red card
    - lvl 5: can't go to green
    - lvl 6: subdued

    Wound:
    - something becomes impossible, eg: broken arm - no sword swinging
    - bleeding - every time you get a red X, and every n minutes, you bruise
    - another wound and you're subdued


----

# Ok, better idea for Melee Combat:

 * ✔✔ v ✔✔ - tie / clash
 * ✔✔ v ✔   - deal a tiredness
 * ✔✔ v ✗   - deal a bruise
 * ✔✔ v ✗✗ - deal a wound

 * ✔ v ✔ - tie / clash - both parties take a tiredness
 * ✔ v ✗ - deal a tiredness
 * ✔ v ✗✗ - deal a bruise

 * ✗ v ✗ - tie /clash - both parties take a bruise
 * ✗ v ✗✗ - deal a tiredness

 * ✗✗ v ✗✗ - ???

Must re-shuffle at 5 cards or lower

If you make a hit after opponent is **fully tired** (down to 10 cards),
 * If already wounded:
  - they're subdued
 * If not:
  - they flip a check for wounded or subdued

### Wounds
bleeding - any time you make an action, flip one card and if it's marked for tiredness, discard it to the tired pile

### General Combat:
 * ✔✔ v ✔✔ - tie / clash
 * ✔✔ v ✔  - hit
 * ✔✔ v ✗  - decisive hit
 * ✔✔ v ✗✗ - critical hit

 * ✔ v ✔  - tie / clash
 * ✔ v ✗  - hit
 * ✔ v ✗✗ - decisive hit

 * ✗ v ✗  - tie /clash
 * ✗ v ✗✗ - hit (this seems not quite right)

 * ✗✗ v ✗✗ - tie / clash

### Ranged Combat:
The secondary effect of ranged combat is that, even when you don't hit an opponent, you can cause them
to stay in the cover they've got, dive for the floor, or interrupt their current action.
Here, we'll call this "pinned"

 * ✔✔ v ✔✔ - exhaust / choose to move
 * ✔✔ v ✔  - pinned (evade)
 * ✔✔ v ✗  - hit & pinned
 * ✔✔ v ✗✗ - critical hit

 * ✔ v ✔✔ - exhaust / choose to move
 * ✔ v ✔  - exhaust or pinned
 * ✔ v ✗  - hit or pinned
 * ✔ v ✗✗ - hit & pinned

 * ✗ v ✔✔ - miss & lose ammo / choose to move
 * ✗ v ✔  - miss & lose ammo
 * ✗ v ✗  - miss
 * ✗ v ✗✗ - miss / pinned

 * ✗✗ v ✔✔ - miss & lose ammo & self-exhaust
 * ✗✗ v ✔  - miss & lose ammo / choose to move
 * ✗✗ v ✗  - miss & lose ammo
 * ✗✗ v ✗✗ - miss & lose ammo / pinned

### Grappling:
Grappling is a kind of long, drawn-out fighting, so I want to make it feel that way.
Upon the successful start of a grapple:
 * The successfull grapple initiation card is placed between the two players.
 * Every turn the character in the inferior position is in the grapple, they:
  * take an exhaust.
  * get 3 chances to flip a their (str? dex?) that matches or beats an open edge of the initiation card
  * if all 4 edges are matched, they break free of the grapple
 * Every turn the character in the superior position is in the grapple, they:
  * do a (str? dex?) check and if successful, exhaust their opponent.

**Grapple Technique skill (a skill to learn):**
 * Every turn the character in the superior position is in the grapple, they:
 * do a (str? dex?) check and if successful, they can choose:
   * deal a blow (bruise instead of exhaust)
   * increase their hold - add this card to the center stack if the symbols can match/beat the outer cards
     * after that is in place, they no longer have to do a skill check to deal blows each turn.

**Grapple Reversal skill (a skill to learn):**
 * if the inferior grappler in one turn gets all 3 flips to match/beat an open edge,
 * they reverse the grapple, and their last laid card is the new grapple initiation card

----

# Ties

```
>>> analyze_contest_notie(d,d,2,2)
({-1: 4970, 1: 5030},
 '49.7% / 50.3%',
  "Ties 20527 (3.1x), {0: '32.6%', 1: '21.6%', 2: '15.2%', 3: '10.6%', 4: '6.8%', 5: '4.1%', 6: '2.9%', 7: '1.9%', 8: '1.6%', 9: '0.9%', 10: '0.5%', 11: '0.4%', 12: '0.3%', 13: '0.2%', 14: '0.1%', 15: '0.1%', 16: '0.1%', 17: '0.1%', 18: '0.0%', 20: '0.0%', 22: '0.0%'}")
```

What this says is that contests between decks where each player has a 2-proficiency bonus could
result in > 20 flips if the rule is "draw 3, take the best, on a tie, do it again".
Flipping 20 times is not going to be fun.

How to mitigate this?

 1. Ties are interpreted by the GM in a way that actually moves the narrative forward - no need to break them
 2. Players can get special "tie breaking" cards that narratively make sense
  * Character luck powers, etc
 3. Greatest count of ✔ marks on the cards (from the flipped suit) wins
  * Counting is annoying though.
  * If that's still tied, then the ✔ marks on all suits
   * If that's still tied, then the least ✗ marks
  * This works pretty well, see `TieCountChecks` in cards.py
   * Suit *X* vs Suit *X* with no mods results in **6%** re-flip
   * Suit *X* vs Suit *Y* with no mods results in **1-3%** re-flip
   * Any time mods are added, even if they're equal, it's **< 1%** re-flip
 4. Calculate the *difference* between proficiencies and flip based on that
  * Counting is annoying though.
  * That'll work for d+2 vs d+2 (calculate as d+0 vs d+0) , but does it give good results across suits? eg, d+2 vs c+1?
   * results: `d2/c2: 72/28`, `d0/c0: 60/40` `d2/c1: 82/18`, `d1/c0: 82/18`, `d2/b2: 78/22`, `d0/b0: 67/33`
   * Nope.

----

# Magic

Doing magic could work by actually performing a magic trick:
 * Declare what the next card is going to be:
 * flip purple side, "it's going to be double-check" - 8/20 chance
 * flip green side, "it's going to be single-check" - 6/20 chance
 * could motivate player to hold off on shuffling
 * therefore, it's advantageous for a caster to memorize stuff & understand the cards
 * BUT - does it make sense thematically in the *tired* deck?
  - sort of if you stipulate that they must guess number of checks


Doing magic could be:
 * Dominion-style deckbuilding
  - Maybe put bond & personality cards into the deck that affect performance
 * Set collection

Doing magic could be:
 * The cards have symbols distributed similarly to Spot-It - there's exactly 2
   symbols that match if you flip 2 cards.

```
Satisfying Array of length 10:
 (maybe in 2 different colors to make 20)
 (requires 20 unique symbols)
 (requires *5* spots to put symbols on the cards)
[
 (0, 1, 2, 3, 4),
 (3, 8, 10, 16, 18),
 (4, 9, 14, 16, 17),
 (0, 7, 9, 11, 18),
 (2, 5, 6, 8, 9),
 (1, 5, 7, 10, 14),
 (4, 7, 8, 15, 19),
 (3, 6, 7, 12, 17),
 (4, 6, 10, 11, 13),
 (0, 8, 12, 13, 14)
]

Satisfying Array of length 10:
 (maybe in 4 different colors to make 20)
 (requires 10 unique symbols)
[[0, 1, 2, 3], (1, 4, 6, 9), (3, 5, 6, 7), (0, 4, 5, 8), (2, 7, 8, 9)]

```

Latter is better because I've only got 4 spots
I could use Chinese Zodiac symbols, but reserve the Dragon and the Goat
Maybe those two could go on blessing / curse cards.

----

# Armor

Maybe they have an armor card that where you can put "bruises" instead of
going to your body.  A couple examples:

 * A "standard armor" card: when taking a bruise, put it in one of 3 slots
   on this card, and take an "exhaustion" instead.
 * A "ethereal carapace" card: when taking a bruise, put it in one of 5 slots
   on this card.  Don't take an exhaustion.
 * A "shield" card: when taking a bruise, succeed a Dex check to put the bruise
   on this card, and take an "exhaustion" instead.


----

# Stuff to add to the face side:
 * Writer's Dice stuff
 * Element symbols
 * Alchemy symbols
 * FUDGE dice

----

# On numbers

 * 0 - Zero is the best number
 * 1 - One is a useful number, as it's the complete opposite of zero,
   without being too big
 * 2 - Two is a fair number, it doesn't take a genuis to do arithmetic
   with it.  Use sparingly.
 * 3 - Allright, three might have some uses, but let's rein in this horse
   before we have a full-blown stampede.
 * 4 - Four is too many. Are you sure you want to use something so
   unweildy? Wouldn't three have sufficed?
 * > 4 - only use these numbers if they promise they will count themselves
   and leave us humans out of it entirely.

----

# Marketing / Slogan

 * The RPG that's ready when you are
 * The RPG that's ready right now

----

Use pre-existing knowledge of Dungeon World and D&D to front-load game
information.

----

Deckahedron World mixes elements from 3 different families of games,
RPGs, contemporary board games, and mad libs.

 * RPGs
   * Asymmetrical jobs - GM / Players
   * Improvisational
     * storytelling / worldbuilding / dialogue / characterization
   * Freedom of choice inside an imagined fictional world
   * Contributing narration or characterization ("playing a role") activates game mechanisms or is mechanically rewarded
 * Contemporary board games
   * Deckbuilding (aka deck management)
     * (the deckahedron)
     * eg, Dominion, A Few Acres of Snow, Legendary
   * Cards that modify and interact with the base rules
     * (the move cards)
     * eg, Dominion, Magic: the Gathering, Yomi
   * Currency engine management
     * (the green token economy)
     * eg, any economic Euro game
   * Resource management / worker placement
     * (the S/W/P mechanism)
     * eg, Agricola, Carcassonne
   * Physical components that feel toy-like
     * cards and tokens
 * Mad Libs
   * blanks as prompts


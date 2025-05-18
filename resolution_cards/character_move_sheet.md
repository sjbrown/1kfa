

# Mix It Up
```python3
attrs = ['Str']
flags = []
levels = []
```

    ✗: 
    ----
    ✓: Deal 1 Might and the foe attacks you
    ----
    ✔: Reveal Might and the foe attacks you
    ----
    ✔✔: Reveal Might and choose

**Details**: On a ✔✔✔, you can choose one:
 * Avoid the foe's attack
 * Add your attack Might

 The foe's attack can be any GM move made directly with that NPC or monster.

 Some attacks may have additional effects depending on the triggering action, the circumstances, or the weapons involved

 Without a melee weapon, a character deals 1 Might.


# Volley
```python3
attrs = ['Dex']
flags = []
levels = ['0', 'g1']
```

    ✗: 
    ----
    ✓: Reveal Might. GM chooses an option.
    ----
    ✔: Reveal Might. Choose an option
    ----
    ✔✔: Reveal Might.

**Details**: Send a volley flying with your ranged weapon.
 Choices:
 * You have to move to get the shot, placing you in danger of the GM's choice
 * You have to take what you can get - halve your Might
 * You have to take several shots - lose 1 PACK


# Parley
```python3
attrs = ['Int']
flags = []
levels = ['0', 'g1']
```

    ✗: 
    ----
    ✓: They demand concrete assurance or exchange, right now. | gray progress
    ----
    ✔: They demand concrete assurance or exchange, right now. | green progress
    ----
    ✔✔: They make a deal. Make a promise and get what you want. | 2x green progress

**Details**: Using leverage, manipulate an NPC. "Leverage" is something they need or want.

 If your leverage is promises or threats without clear evidence, flip with 1 level of disadvantage.
    


# Defy Danger
```python3
attrs = ['Str', 'Dex', 'Int']
flags = []
levels = []
```

    ✗: 
    ----
    ✓: Make progress, but stumble, hesitate, flinch or pay a cost.
    ----
    ✔: You do it, but there's a new complication
    ----
    ✔✔: Success

**Details**: When you act despite an imminent threat, say how you deal with it and flip.
 If you do it...
 * by powering through or enduring, flip Str
 * by getting out of the way or acting fast, flip Dex
 * with quick wits or via mental fortitude, flip Int

 On a ✅ / ✔✔, the GM may ask you a question, offer you a worse outcome, hard bargain, or ugly choice
    


# Defend
```python3
attrs = ['Str']
flags = []
levels = []
```

    ✗: 
    ----
    ✓: Choose how to split the Might of the attack between yourself and the thing you defend
    ----
    ✔: Spend 1 XP, Choose 1
    ----
    ✔✔: Spend 1 XP, Choose 2

**Details**: Stand in defense of a person, item, or location that is under attack. The attack is redirected from the thing you defend to yourself. You may spend XP to choose:
 * Halve the attack's effect or damage
 * Open up the attacker to an ally giving +1 advantage against the attacker
 * Attack them with your Might

 This move can interrupt an attack against an ally if you are in range and Might has not yet been revealed.

 Place a green token on this card until you Take a Breather
    


# Discern
```python3
attrs = ['Int']
flags = []
levels = []
```

    ✗: 
    ----
    ✓: Ask the GM 1 question from the list
    ----
    ✔: Ask the GM 2 questions from the list
    ----
    ✔✔: Ask the GM 3 questions from the list

**Details**: Closely study a situation or person, ask the GM your question(s). For each question, place a green token on this card. Whenever the information gained is acted upon by anyone in the party, take +1 advantage and remove a token from this card.
 * What here is useful or valuable to me?
 * What happened here recently?
 * What is about to happen?
 * What should I be on the lookout for?
 * Who's really in control here?
 * What here is not what it appears to be?
    


# Unfold Mystery
```python3
attrs = ['Int']
flags = []
levels = []
```

    ✗: 
    ----
    ✓: Create a one-unit stake in the new scene with the newly understood information. | one gray progress
    ----
    ✔: Create a one-unit stake in the new scene with the newly understood information. | one green progress
    ----
    ✔✔: Create a two-unit stake in the new scene with the newly understood information. | two green progress

**Details**: State facts about the world or the people in it.
 Consult your accumulated knowledge about something.

 (You may always do this through the normal course of playing the game, but when the GM doubts the fact or judges that the fact would provide significant benefit to the players, the Unfold Mystery move is triggered)

 On a ✅, the GM may ask you "How do you know this?".
    


# Rest
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: When not travelling, with a day to devote to rest, do the following:

 * Step 1: Return all Exhaustion tokens to the supply
 * Step 2: Count the Harm and Wound tokens on your Exhaustion pile
 * Step 3: Keep that many cards in your Exhaustion pile, put the rest into your discard pile
 * Step 4: Return one Harm token to the supply
 * Step 5: Say who you blame for your injuries

 Magic items left idle regain their charges up to their capacity

 Gird all your armour
 (remove Harm and Wound tokens from it)

 Learning skills, studying, or any action that takes mental or physical effort is not available when Resting.
    


# Seek Help
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: When in a peaceful environment where external resources with healing powers are available:

 * Step 1: Describe your healing experience
 * Step 2: Return all Exhaustion tokens to the supply
 * Step 3: Return all Harm tokens to the supply
 * Step 4: Count the Wound tokens on your Exhaustion pile
 * Step 5: Keep that many cards in your Exhaustion pile, put the rest into your discard pile
 * Step 6: Return all Wound cards to the supply
 * Step 7: Say who you are closer to forgiving
 * Step 8: If you are at The Hearth, return all Wound tokens to the supply

 As with Rest, idle magic items regain their charges. Gird all your armour. Seeking Help leaves no time for activities that take effort.
    


# Take a Breather
```python3
attrs = ['INT', 'DEX']
flags = []
levels = []
```

    ✗: GM Move
    ----
    ✓: New complication. See below.  Regain 2 exhausted cards of your choice | gray progress
    ----
    ✔: Find a strategic safe spot / avoid attention.  Regain 2 exhausted cards of your choice | green progress
    ----
    ✔✔: Find a strategic safe spot / avoid attention.  Regain 2 exhausted cards of your choice | 2x green progress

**Details**: Spend an uninterrupted moment to catch your breath.
You can't Take a Breather twice in a row.
Flip Int to find a strategic safe spot. On failure: There's something wrong with the spot
Flip Dex to avoid attention. On failure: Foe moves to a spot where you're disadvantaged

At the moment you're safe and exit the action (combat is over, pursuit ends), you can flip Str and Take a Breather as a Fast move.
    


# Bravely Run Away
```python3
attrs = []
flags = ['UNENCUMBERED']
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: See SVG

As long as you're not cornered or surrounded, escape your foes.

The GM either starts a Pursuit Interlude or answers the question:

 * Where does the character end up?

Encumbrance Penalty: Count up all your Item and Pack cards.
 *  If you have less than 3, regain 2 Stamina points
 *  If you have 3-4, expend 1 stamina point
 *  If you have 5-6, expend 2 stamina points
 *  If you have more than 6, expend 3 stamina points



# Destiny Forewritten
```python3
attrs = []
flags = ['IMMEDIATE']
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: After you flip, and before the GM describes the consequence of that flip, declare "I invoke Destiny".

Start the flashback by spending 1 XP and describing how something in the character's past prepared them for this situation. Then ignore the original flip and flip again (using the same advantage / disadvantage as before).

After that, spend XP 1-for-1 to bump up the result
    


# Good thing I brought...
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: See SVG

Spend (2 Pack) and answer:

 * What equipment did you bring along to aid in the current situation?
 * What was consumed or broken?

OR

Spend (1 XP + 1 Pack) and answer:

 * What equipment did you bring along to aid in the current situation?


# Study under a master
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Spend your day in town learning new skills.

Spend 2 XP and tell a story with the GM about how you found a teacher who helped you improve your skills.

Choose:
 *  Level up in a move -- place a green card on it. 
 *  Gain new skills -- take a new move card
    


# Shop / Procure
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Spend your day in town in the acquisition of new gear. The GM will tell you who is selling and hand you 4 cards from the Item deck. To keep one of the cards, you must buy or barter.
Choose:
 *  Spend 1 PRECIOUS Pack 
 *  Spend 1 XP + 1 Pack 
 *  Spend 1 XP + 1 of your Item cards

Any gained magic items have capacity for just 1 charge.

Also, any time you're in town, you can spend 1 PRECIOUS Pack card to gain 2 normal Pack cards
    


# Tales of a Weapon
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Spend 2 XP.

Together with the GM, make a new weapon card with More Power than your current weapon.  The GM will offer it to you as one of the Item cards at your next Shop / Procure or make it available as loot in your next adventure.

Spend 1 more XP to add a magical power (capacity: 1 charge) to the weapon, and the GM will add a weakness or downside.
    


# Sharpen & Stitch
```python3
attrs = ['INT']
flags = []
levels = ['0', 'g1']
```

    ✗: GM Move
    ----
    ✓: Spend Pack at a rate of 2-to-1 to remove red cards | gray progress
    ----
    ✔: A Pack spent may remove 1 red card | green progress
    ----
    ✔✔: A Pack spent may remove 2 red cards | 2x green progress

**Details**: While resting, spend Pack to repair damage to items.

At a town, you may forego the flip, and together with the GM, decide who there is willing to fully repair all of your items in exchange for one of your cards that they find Precious.
    


# Critical Flip
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: After a flip, if the card that resolves the flip is the Critical Success card (with the green ring in the center), you may:

Take a Blessing card from the supply and put it in your discard pile

Or,

Say how your character's practice has finally paid off, or how they had an insight or epiphany about the move they just accomplished. Spend XP 1-for-1 to go up levels in the move that was just resolved.
    


# Good Cardio
```python3
attrs = ['STR']
flags = ['IMMEDIATE']
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: Shadow point
    ----
    ✓: Regain 1 exhausted card of your choice.  Your foe moves to a position of advantage.
    ----
    ✔: Regain 1 exhausted card of your choice.  Your foe moves to a position of advantage.
    ----
    ✔✔: Regain 1 exhausted card of your choice

**Details**: Take one deep breath to recover Stamina as you jump into the fray.
When you would expend Stamina from physical effort, put token(s) on this card's slots instead.
    


# And This Is For...
```python3
attrs = ['STR']
flags = ['IMMEDIATE']
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: Shadow point
    ----
    ✓: 
    ----
    ✔: 1 Might
    ----
    ✔✔: Reveal 1-4 Might. Place a token on this card until you Take a Breather

**Details**: After successfully striking a foe in melee, intone the name of who you avenge or protect, and add a punch, kick, or shove.
    


# Where It Hurts
```python3
attrs = ['DEX', 'STR']
flags = ['IMMEDIATE']
levels = ['r1', '0', 'g1']
```

    ✗: Shadow point
    ----
    ✓: 
    ----
    ✔: 1 red token
    ----
    ✔✔: 2 red tokens max.

**Details**: When you reveal Might, say how your attack was focused on a part of the foe's body. You may turn points of Might into red tokens that are placed on a marker representing this foe. Afterwards, any player can discard one of those red tokens to take +1 advantage against the foe.
    


# Tied with Her Ribbon
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Put this card behind your favourite weapon card. This weapon has been decorated with a trinket from someone you've known since birth.

Your encumbrance penalty for this weapon is one fewer than normal.

If separated from your weapon, say how thinking of her reminds you of who you are or the people you come from and every move that aids your reunion with your weapon gets +1 advantage.
    


# Like A Second Skin
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: See SVG
    
The Encumbrance Penalty for your armor is one less than usual.

Level 2: The Encumbrance Penalty for your shield is one less than usual.
Slot for 1 harm

Level 3: Your armour does not count for the encumbrance penalty.
Slot for 1 harm OR 1 wound


# Go Berserk!
```python3
attrs = []
flags = ['IMMEDIATE']
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Fly into an enraged state! Plans be damned and hazards damned twice! Let spill your wrath!

While enraged, take +1 advantage when using Str. But, you are unable to perform any move requiring Int.

To regain your wits, you must Take a Breather.
    


# Bloody But Unbowed
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: See SVG

Add +1 to your attack Might for every Harm token you have,
including every Harm token on this card's slots



# Mystic Breathwork
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: See SVG
    


# It Belonged to My Father
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Put this card behind an armour or shield card. It is marked with a symbol of the person who taught you the ropes or was supposed to protect you.

Your encumbrance penalty for this shield or armour is one fewer than normal

When someone stands in your way, or you face a dangerous threshold, answer and proceed. Then the GM answers the second question

*  How did this armour or symbol will earn you passage? 
 *  Does the armour need to be surrendered or destroyed?
    


# Apex Predator
```python3
attrs = ['Int', 'Str']
flags = []
levels = []
```

    ✗: 
    ----
    ✓: Answer one question. Expend 1 Stamina.
    ----
    ✔: Answer one question.
    ----
    ✔✔: Answer one question. | green progress

**Details**: Make contact with, and hold your own against, the spirit of a wild beast.

Place a green token on this card until you Take a Breather

While this token remains,

During combat, take + 1 advantage when you Discern or look for a Weak Spot

If you are in pursuit of a fleeing or hidden foe, take +1 advantage to Called Shot or It's a Trap!

Questions:

 * What hunger does the spirit transmit?
 * What sense feels sharper?
 * What sacrifice does the spirit demand?




# Intimidate
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: For Parley against a target whose stare you can meet unflinchingly, flip Str as well as Int. Take the best result

Or, when an ally is Parleying, loom imposingly nearby.  Flip Str and if it's better than your ally's Parley flip, they may use your result.
    


# Fury
```python3
attrs = ['STR']
flags = ['IMMEDIATE']
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: Shadow point
    ----
    ✓: Add 1 Might
    ----
    ✔: Add your attack Might, divided by 2. Keep a token on this card until you Take a Breather
    ----
    ✔✔: Add your attack Might. Keep a token on this card until you Take a Breather

**Details**: After successfully striking a foe in melee, describe how the attack was especially furious, or you used your weapon to strike again.
    


# Goreography
```python3
attrs = ['DEX']
flags = ['IMMEDIATE']
levels = ['r1', '0', 'g1']
```

    ✗: Shadow point
    ----
    ✓: GM Chooses 1.  Turn this card face-down until you Take a Breather
    ----
    ✔: Choose 1.  Turn this card face-down until you Take a Breather
    ----
    ✔✔: Choose 2.  Turn this card face-down until you Take a Breather

**Details**: After successfully striking a foe in melee, flip and choose. You may choose an option more than once. Choices:
 *  hit another foe during your attack 
 *  disable your foe's armour 
 *  disarm your foe
    


# It's a Trap!
```python3
attrs = ['INT']
flags = []
levels = ['r2', 'r1', '0', 'g1']
```

    ✗: GM Move
    ----
    ✓: Place 1 token on this card | gray progress
    ----
    ✔: Place 2 tokens on this card | green progress
    ----
    ✔✔: Place 3 tokens on this card | 2x green progress

**Details**: Spend a moment to survey a dangerous area for traps, ambushes and secrets. Flip to supply this card with tokens. Spend the tokens 1-for-1 as you go warily onward to ask these questions:
 *  Is there a hidden danger here and if so, what activates it? 
 *  What does the hidden danger do when activated? 
 *  What else is hidden here? 
 *  How can the danger be disabled?
    


# Pick Pockets
```python3
attrs = ['DEX']
flags = ['UNENCUMBERED']
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: GM Move
    ----
    ✓: gray progress
    ----
    ✔: The GM will offer you two options between suspicion, danger, or cost | green progress
    ----
    ✔✔: Success | 2x green progress

**Details**: While they're not looking at you, unburden someone of something they're carrying

Encumbrance Penalty: expend stamina points from mental exhaustion. Count up all your Item and Pack cards.
*  If you have 3-4, expend 1 stamina point 
 *  If you have 5-6, expend 2 stamina points 
 *  If you have more than 6, expend 3 stamina points
    


# Pick Locks
```python3
attrs = ['DEX']
flags = []
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: GM Move
    ----
    ✓: gray progress
    ----
    ✔: The GM will offer you two options between suspicion, danger, or cost | green progress
    ----
    ✔✔: Success | 2x green progress

**Details**: A "key" is just a little brass stick with some cleverness carved into it. If you've brought your own cleverness, then any stick will do.

Flip Dex, or do the Pick Locks mini-game.
    


# Backstab
```python3
attrs = ['DEX']
flags = ['UNENCUMBERED']
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: GM Move
    ----
    ✓: gray progress
    ----
    ✔: Choose 1 | green progress
    ----
    ✔✔: Choose 2 | 2x green progress

**Details**: Attack a surprised or defenseless foe with a melee weapon. Choices:
 *  You don’t get into melee with them 
 *  Attack them with your attack Might + 1-6 Might
 *  You create a +1 advantage for the next player who attacks this foe 
 *  Reduce their attack Might one step

Encumbrance Penalty: You cannot perform this move if your count of Item and Pack cards is more than 3
    


# Weak Spot
```python3
attrs = ['INT']
flags = ['IMMEDIATE']
levels = ['r2', 'r1', '0', 'g1']
```

    ✗: Shadow point
    ----
    ✓: Choose 1
    ----
    ✔: Choose 1
    ----
    ✔✔: Choose 2

**Details**: Scope out a foe with your perspicacious eyes and declare what weakness you observed

Choices:
 * When anyone attacks this weakness, they add 1-4 Might
 * When the weakness is first attacked, take +1 advantage.
 * 1 green progress


# Bum Rush
```python3
attrs = ['DEX', 'STR']
flags = []
levels = ['r1', '0', 'g1', 'g2']
```

    ✗: GM Move
    ----
    ✓: Choose 1 and the foe manages 1 Might against you | gray progress
    ----
    ✔: Choose 1 | green progress
    ----
    ✔✔: Choose 2 | 2x green progress

**Details**: See SVG

Before you are engaged in melee, charge in (expend Stamina) and then choose:

 * Move past them out of their reach
 * Fast strike before the melee begins: attack a foe with your Might
 * perform another move right now, ignoring its Encumbrance Penalty


# Find Shadows
```python3
attrs = []
flags = ['UNENCUMBERED']
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Nighttime or indoors, while no foe is bearing down on you, say what darkness you find shelter in. Take a Breather, but forgo the flip and simply regain 1 exhausted card. In addition, foes cannot see you until you move.

Encumbrance Penalty: expend stamina points from mental exhaustion. Count up all your Item and Pack cards.
*  If you have 3-4, expend 1 stamina point 
 *  If you have 5-6, expend 2 stamina points 
 *  If you have more than 6, expend 3 stamina points
    


# I'm Only Here for the Job
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: When an adventure or heist gains you a new precious item, seek out a seedy contact in town. The GM will tell you who you meet. Spend one precious item and choose 2
 *  Learn an enemy's disposition 
 *  get leverage on a PC or NPC 
 *  gain a magic item card you can keep secret from everyone, even the GM

If you are ever offered payment to betray the party, you must destroy or leave behind all your precious items to deny the payment.
    


# Slide
```python3
attrs = []
flags = ['UNENCUMBERED']
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Spend 1 XP and describe how the environment or recent events provided a distraction that let you escape the attention of any foes around you.

Answer honestly: Do they even remember seeing you there?

Encumbrance Penalty: expend stamina points. Count up all your Item and Pack cards.
*  If you have 3-4, expend 1 stamina point 
 *  If you have 5-6, expend 2 stamina points 
 *  If you have more than 6, expend 3 stamina points
    


# Called Shot
```python3
attrs = ['DEX']
flags = []
levels = ['r2', 'r1', '0', 'g1']
```

    ✗: GM Move
    ----
    ✓: gray progress
    ----
    ✔: 1 Might. Choose an option | green progress
    ----
    ✔✔: Reveal Might (or choose 1 Might) and choose an option | 2x green progress

**Details**: Name a specific target you're aiming for when you attack at range.
 *  Head: add a second Might reveal
 *  Arms: They drop anything they're holding
 *  Legs: They're hobbled and slow moving
 *  Other: GM will say what happens

If the target is surprised or defenseless, flip with one level of advantage.
    


# Come and get me
```python3
attrs = ['INT']
flags = []
levels = ['r1', '0', 'g1', 'g2']
```

    ✗: You succumb to a danger you did not see | GM Move
    ----
    ✓: They see your plan and respond | gray progress
    ----
    ✔: They succumb to the danger's effects | green progress
    ----
    ✔✔: They succumb to the danger and cannot respond to your next action | 2x green progress

**Details**: Put an environmental hazard between you and a foe and goad them to approach.

On ✗: you succumb to a danger you did not see
    


# Not On My Turf
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: While in a pursuit, spend 1 XP and describe one way the chase is about to change:
 *  we go above 
 *  we go below 
 *  the air changes 
 *  the earth changes 
 *  the water changes
    


# Derring-Do
```python3
attrs = ['DEX']
flags = []
levels = ['r2', 'r1', '0', 'g1']
```

    ✗: GM Move
    ----
    ✓: You arrive, the GM will say why this is more tenuous than you originally thought | gray progress
    ----
    ✔: You arrive, but the GM will say what it cost you | green progress
    ----
    ✔✔: Smooth move | 2x green progress

**Details**: Name a (setting appropriate) aspect of the environment that the GM hasn't described yet. Make it something that will help you get into an advantageous position. Jump, clamber, swing, etc. to that position.
    


# Sangfroid
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: When you would expend Stamina from mental exhaustion, put Exhaustion tokens on this card instead
    


# Use a Magic Item
```python3
attrs = ['INT']
flags = ['RECEIVE CARDS']
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: The spell / effect fails. The GM will say how | GM Move
    ----
    ✓: The spell / effect is cast, GM chooses | gray progress
    ----
    ✔: The spell / effect is cast and choose | green progress
    ----
    ✔✔: The spell / effect is successfully cast | 2x green progress

**Details**: Lose 1 charge.

Choices:
 *  lose 1 charge on all your other magic items 
 *  reduce the charge capacity of this item by 1

On ✗: the effect fails or misfires, the GM will say how
    


# Entreat the Blood-Bound
```python3
attrs = []
flags = ['RECEIVE CARDS']
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: Carefully sacrifice your blood.

Place a green token on this card and take a Wound card into your Discard pile.

When you Rest or Seek Help, you may return the token and the Wound card.

Until the Wound is healed, using magical items does not cost the usual 1 charge (though charges may be lost via other effects)

What does it sound or smell like when you do this?

Also, Blade of Echoes does not count for your encumbrance penalty


# Channel the Living Light
```python3
attrs = ['INT']
flags = ['RECEIVE CARDS']
levels = ['r2', 'r1', '0', 'g1']
```

    ✗: GM Move
    ----
    ✓: Expend 3 Stamina | gray progress
    ----
    ✔: Expend 2 Stamina | green progress
    ----
    ✔✔: Expend 2 Stamina, take a Blessing Card | 2x green progress

**Details**: See SVG

Use this instead of *Use a Magic Item*
Instead of losing charges, expend Stamina due to mental exhaustion.

Answer:

 * What does it look like when you channel?

Sigil of the Living Light does not count for your Encumbrance Penalty.
    


# Unknown Benefactor
```python3
attrs = []
flags = ['IMMEDIATE']
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: A mysterious magical defense instantaneously cancels any attack against you, but you must end an ONGOING magical effect of your magic item and lose all its remaining charges.

Any amount of Might may be cancelled, any narrative effects of the attack will be resolved by the GM.

Anytime afterward, confront an authority as being your unknown benefactor. The GM will explain why you're correct, and must spend:
 *  1 Journey Point and you keep the card 
 *  3 Shadow Points and you lose the card
    


# Void Transfusion
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: See SVG.

When you Entreat the Blood-Bound, also recharge all of your magic items that have been depleted.

If the cards are recharged above their capacity, place that number of white-side green cards on them.
    


# Reach Out With Your Feelings
```python3
attrs = ['Int']
flags = []
levels = []
```

    ✗: 
    ----
    ✓: Answer one question. Expend 1 Stamina.
    ----
    ✔: Answer one question.
    ----
    ✔✔: Answer one question. | green progress

**Details**: Maintaining skin contact with an undepleted magical item, attune to the universe.

Place a green token on this card until you Take a Breather

While this token remains,

You have an extra split-second reaction time. Lose 1 fewer Stamina from physical exhaustion when attacked.

You can share mindful wisdom with an ally while they perform Called Shot or It's a Trap!, and they get +1 advantage

 * What forms are suggested by the universe's rippling?
 * What covert malice hides under overt compassion?
 * What covert compassion hides under overt malice?


# Fundamental Magic
```python3
attrs = ['INT']
flags = []
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: GM Move
    ----
    ✓: Expend 3 Stamina, put this card face-down until you rest | gray progress
    ----
    ✔: Expend 2 Stamina, put this card face-down until you rest | green progress
    ----
    ✔✔: Expend 1 Stamina | 2x green progress

**Details**: Without need of a magic item, cast a spell having the effect of a magic item you've seen before. Describe what it takes out of you.

Flip Int or do the Fundamental Magic mini-game
    


# Counterspell
```python3
attrs = ['INT']
flags = []
levels = ['r2', 'r1', '0', 'g1']
```

    ✗: GM Move
    ----
    ✓: The spell is countered, the item is depleted | gray progress
    ----
    ✔: The spell is countered, the item loses a charge | green progress
    ----
    ✔✔: The spell is countered and has no effect on you | 2x green progress

**Details**: When you attempt to counter a magical effect that will otherwise affect you, stake one undepleted magical item on the defense and flip
    


# Breach the Dam
```python3
attrs = ['INT']
flags = []
levels = ['r2', 'r1', '0', 'g1', 'g2']
```

    ✗: The item is destroyed | GM Move
    ----
    ✓: The item is depleted.  Expend 2 stamina from mental exhaustion | gray progress
    ----
    ✔: The item is depleted | green progress
    ----
    ✔✔: The item loses 1 charge | 2x green progress

**Details**: Use this instead of Use a Magic Item. Describe a new source (neither the Blood-Bound nor the Living Light) of magical energy in the universe that rushes into your magical item. Choose:
 *  ignore its limitations 
 *  double its effects

The effects happen no matter what.
On ✗: The item is destroyed and you are marked by the new source.
    


# Obsessive Contemplation
```python3
attrs = []
flags = []
levels = []
```

    ✗: 
    ----
    ✓: 
    ----
    ✔: 
    ----
    ✔✔: 

**Details**: In town, spend up to 3 XP and a full day doing nothing but investigating or experimenting on your items. For each XP spent, choose a new ✷.

If it is a magic item, choose:
 *  it is augmented with a new magical effect from an item you've seen before 
 *  it gains capacity for an additional charge 
 *  it gains More Power

If it is a Precious item: 
 *  it is imbued with a new magical effect from an item you've seen before, with one charge capacity

If it is a weapon, choose: 
 *  it gains More Power 
 *  its appearance has magically changed 
 *  it is imbued with a magical effect from an item you possess, with one charge capacity
    


# Suggestive Subtlety
```python3
attrs = ['INT']
flags = []
levels = ['r2', 'r1', '0', 'g1']
```

    ✗: GM Move
    ----
    ✓: Spend 1 XP, expend 1 Stamina | gray progress
    ----
    ✔: Spend 1 XP, expend 1 Stamina | green progress
    ----
    ✔✔: Spend 1 XP | 2x green progress

**Details**: First, get their attention. Then, without saying it outright, but by mysterious wiles and unspoken language, change an NPC's mind. Describe your tricks and say what you changed:
 *  They strongly believe a new fact 
 *  They judge an old belief to be a lie 
 *  They ignore a previous concern 
 *  They are focused on a new goal
    

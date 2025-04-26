from rapidfuzz import process, fuzz

authenticity_keywords = [
    "honest", "genuine", "sincere", "trustworthy", "integrity",  
    "transparent", "authentic", "credible", "dependable", "reliable",  
    "ethical", "real", "truthful", "verifiable", "legitimate",  
    "candid", "straightforward", "honorable", "faithful", "loyal",  
    "accurate", "valid", "factual", "unbiased", "original",  
    "pure", "unadulterated", "principled", "scrupulous", "consistent",  
    "forthright", "unfeigned", "bona fide", "genuineness", "accurate",  
    "fair", "just", "uncorrupted", "earnest", "trustable",  
    "sincerity", "realistic", "truth-bearing", "objective", "unchanged",  
    "undistorted", "untainted", "authoritative", "faithworthy", "righteous",  
    "unembellished", "unmodified", "unpretentious", "untarnished", "unadulterated",  
    "unimpeachable", "verifiable", "legitimate", "reputable", "sound",  
    "authenticity", "wholesome", "genuine nature", "straight-shooting", "reliable",  
    "high integrity", "trustable", "dependability", "truthful expression",  
    "undeniable", "unquestionable", "undistorted", "rightful", "consistent",  
    "proven", "uncontaminated", "true-to-life", "credible source", "dependable resource",  
    "validity", "unadulterated truth", "true-hearted", "trust-driven", "unpretentious",  
    "no-nonsense", "unclouded", "unmasking", "verified", "balanced",  
    "unshakable", "authentic value", "grounded", "without fabrication",  
    "non-manipulated", "unconstrained", "unforced", "unspoiled", "unrefined"
]

def detect_authenticity(text, authenticity_keywords, similarity_threshold=80):
    authenticity_count = 0

    for keyword in authenticity_keywords:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            authenticity_count += 1
    
    total_words = len(text.split())

    if authenticity_count == 0:
        return {
            "Message": "No authenticity signals detected",
            "Authenticity Keywords": 0,
            "Total Words": total_words,
            "Authenticity Level": "Neutral"
        }
    authenticity_ratio = authenticity_count / total_words

    if authenticity_ratio > 0.2:
        authenticity_level = "Highly authentic (consistent use of authenticity-related words)"
    elif authenticity_ratio > 0.1:
        authenticity_level = "Moderately authentic"
    else:
        authenticity_level = "Low authenticity detected (minimal use of authenticity-related words)"

    result = {
        "Authenticity Keywords": authenticity_count,
        "Total Words": total_words,
        "Authenticity Ratio": round(authenticity_ratio, 2),
        "Authenticity Level": authenticity_level,
    }
    return result

positive_emotions = [
    "happy", "joyful", "excited", "grateful", "content", "proud",  
    "enthusiastic", "cheerful", "elated", "love", "optimistic",  
    "blissful", "ecstatic", "thrilled", "euphoric", "hopeful",  
    "serene", "peaceful", "satisfied", "radiant", "thankful",  
    "compassionate", "affectionate", "tender", "warm-hearted", "cheery",  
    "lighthearted", "buoyant", "spirited", "uplifted", "inspired",  
    "exhilarated", "exuberant", "vivacious", "overjoyed", "delighted",  
    "glad", "jubilant", "fulfilled", "harmonious", "flourishing",  
    "positive", "passionate", "appreciative", "encouraged", "motivated",  
    "hope-filled", "adored", "ecstatic", "wonderstruck", "merry",  
    "joyous", "playful", "radiating", "charmed", "graceful",  
    "giddy", "contented", "jolly", "gleeful", "sunny",  
    "vivified", "heartening", "revitalized", "buoyed", "soothed",  
    "enlivened", "rejuvenated", "mesmerized", "trusting", "secure",  
    "strong", "bold", "free", "carefree", "blessed",  
    "exultant", "elevated", "soulful", "bright", "kindhearted",  
    "open-hearted", "generous", "friendly", "sympathetic", "reassured",  
    "radiant", "uplifted", "bubbling", "enthused", "invigorated",  
    "revived", "cheerful-minded", "seraphic", "chipper", "ecstatic",  
    "lively", "comforted", "vibrant", "invincible", "mirthful",  
    "tranquil", "playful-minded", "renewed", "optimistically charged",  
    "blessed with peace", "thankful-hearted", "secure in spirit", "amused",  
    "refreshed", "elevated", "joy-spread", "hopeful-minded", "glorious",  
    "deeply happy", "enchanted", "elated", "enchanted", "thrilled to the core",  
    "gratefully alive", "gleaming", "soulfully content", "refueled",  
    "buoyed up", "encouraging", "mellow", "untroubled", "loved",  
    "emotionally enriched", "spirited", "radiantly calm", "warmly fulfilled"
]

negative_emotions = [
    "sad", "angry", "frustrated", "upset", "disappointed", "guilty", "worried",  
    "anxious", "depressed", "miserable", "hate", "jealous", "regret",  
    "resentful", "bitter", "lonely", "hopeless", "desperate",  
    "heartbroken", "grief-stricken", "melancholy", "sorrowful", "despondent",  
    "fearful", "insecure", "ashamed", "humiliated", "mortified",  
    "embarrassed", "distraught", "overwhelmed", "stressed", "exhausted",  
    "irritated", "annoyed", "vengeful", "furious", "infuriated",  
    "rageful", "disgusted", "rejected", "neglected", "ignored",  
    "pessimistic", "despondent", "unhappy", "desolate", "abandoned",  
    "mournful", "troubled", "gloomy", "low-spirited", "defeated",  
    "powerless", "helpless", "agitated", "disturbed", "shaken",  
    "suffocated", "alienated", "lost", "disoriented", "unsettled",  
    "nervous", "apprehensive", "doubtful", "uneasy", "pressured",  
    "distressed", "panicked", "traumatized", "wretched", "grouchy",  
    "moody", "weary", "dreadful", "horrified", "sullen",  
    "withdrawn", "vindictive", "hostile", "spiteful", "remorseful",  
    "pained", "vulnerable", "burned-out", "forsaken", "shamed",  
    "angst-ridden", "numb", "cold-hearted", "forsaken", "stuck",  
    "unworthy", "insignificant", "misunderstood", "dismayed", "conflicted",  
    "distrustful", "resentful", "shattered", "abhorred", "hollow",  
    "paralyzed", "devastated", "traumatized", "inconsolable", "despondent",  
    "overcome with guilt", "broken-hearted", "stressed-out", "baffled",  
    "helplessly lost", "unloved", "isolated", "struggling", "empty",  
    "angry with self", "unfulfilled", "hopelessly lost", "forlorn",  
    "depressed beyond measure", "unsettling", "tormented", "insufferable",  
    "sickened", "lost in thought", "paranoid", "irate", "anxiety-ridden",  
    "overburdened", "livid", "thwarted", "unheard", "disconnected",  
    "nervously charged", "distracted", "apprehensive", "strained",  
    "hopelessly confused", "heart-wrenching", "crying out", "overcome",  
    "devastated beyond repair", "angst-laden", "disillusioned", "misaligned",  
    "disenchanted", "regretful", "infuriated", "infantile", "dejected"
]

def consistency_of_emotion(text, positive_emotions, negative_emotions, similarity_threshold=80):
    positive_count = 0
    negative_count = 0

    for keyword in positive_emotions:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            positive_count += 1

    for keyword in negative_emotions:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            negative_count += 1    

    total_emotion_words = positive_count + negative_count
    if total_emotion_words == 0:
        return {
            "Message": "No emotional tone detected",
            "Positive Words": 0,
            "Negative Words": 0,
            "Total Emotion Words": 0,
            "Consistency": "Neutral tone detected"
        }
    positive_ratio = positive_count / total_emotion_words
    negative_ratio = negative_count / total_emotion_words

    if positive_ratio > 0.7:
        consistency = "Strongly positive emotional tone detected"
    elif negative_ratio > 0.7:
        consistency = "Strongly negative emotional tone detected"
    elif 0.4 <= positive_ratio <= 0.6:
        consistency = "Balanced emotional tone detected (equal mix of positive and negative emotions)"
    else:
        consistency = "Inconsistent emotional tone detected (slight dominance of one type)"

    balance_difference = abs(positive_ratio - negative_ratio)

    if balance_difference < 0.2 and total_emotion_words > 10:
        consistency = "Highly dynamic emotional tone detected (frequent emotional shifts)"
    elif balance_difference < 0.1:
        consistency = "Highly balanced emotional tone detected"

    result = {
        "Positive Words": positive_count,
        "Negative Words": negative_count,
        "Total Emotion Words": total_emotion_words,
        "Positive Ratio": round(positive_ratio, 2),
        "Negative Ratio": round(negative_ratio, 2),
        "Balance Difference": round(balance_difference, 2),
        "Consistency": consistency,
    }
    return result

positive_opinion = [
    "love", "like", "enjoy", "prefer", "agree", "approve", "support", "recommend",  
    "admire", "appreciate", "endorse", "favor", "praise", "value",  
    "respect", "embrace", "cherish", "delight in", "applaud",  
    "trust", "commend", "celebrate", "adore", "recognize",  
    "esteem", "encourage", "advocate", "idolize", "approve of",  
    "highly regard", "look up to", "hold in high esteem", "stand by", "favorably view",  
    "think highly of", "find appealing", "consider excellent", "rate highly", "back",  
    "be a fan of", "go for", "support wholeheartedly", "have a soft spot for", "stand behind",  
    "be impressed by", "be fond of", "speak highly of", "have confidence in", "deem worthy",  
    "see value in", "find valuable", "appraise positively", "be enthusiastic about", "hold dear",  
    "find admirable", "regard positively", "be captivated by", "warmly embrace", "approve wholeheartedly",  
    "stand in favor of", "revere", "worship", "treasure", "be devoted to",  
    "glorify", "honor", "laud", "extol", "exalt", "magnify",  
    "appraise highly", "speak favorably of", "find delightful", "be passionate about", "hail",  
    "marvel at", "put trust in", "give credit to", "appreciate greatly", "rejoice in",  
    "salute", "venerate", "enjoy thoroughly", "champion", "boast about",  
    "acknowledge positively", "hold in the highest regard", "rave about", "elevate", "applaud enthusiastically",  
    "place faith in", "enthuse over", "be deeply moved by", "show admiration for", "approve beyond doubt",  
    "perceive favorably", "validate", "defend", "stand up for", "be won over by",  
    "express delight for", "honor with praise", "be enamored with", "speak glowingly of", "sing praises of",  
    "highlight positively", "commend as excellent", "vouch for", "recommend wholeheartedly", "be thrilled by",  
    "find inspiring", "hold close to heart", "exude positivity for", "stand as a proponent of", "bask in admiration for",  
    "enthusiastically acknowledge", "exhibit devotion to", "endorse strongly", "relish", "find impressive",  
    "proclaim fondness for", "cherish deeply", "be overwhelmed with appreciation for", "warm up to", "cheer for",  
    "perceive as outstanding", "feel affection for", "see as praiseworthy", "smile upon", "show deep appreciation for"
]

negative_opinion = [
    "hate", "dislike", "avoid", "oppose", "disagree", "criticize", "reject", "condemn",  
    "detest", "despise", "abhor", "resent", "distrust", "disapprove",  
    "object to", "deplore", "loathe", "scorn", "disdain",  
    "rebuke", "reproach", "denounce", "dismiss", "discount",  
    "discredit", "disregard", "disbelieve", "protest against", "find fault with",  
    "scoff at", "mock", "ridicule", "undermine", "boycott",  
    "shun", "spurn", "turn down", "scold", "berate",  
    "criticize harshly", "castigate", "vilify", "demonize", "sneer at",  
    "oppugn", "deprecate", "disparage", "belittle", "condescend to",  
    "minimize", "brush off", "push back against", "revolt against", "repudiate",  
    "disgust", "naysay", "condemn outright", "find unacceptable", "frown upon",  
    "reject outright", "take issue with", "have no respect for", "be against", "hold in contempt",  
    "strongly disagree", "turn one's back on", "see no value in", "think poorly of", "not tolerate",  
    "look down on", "find offensive", "be unimpressed with", "be skeptical of", "not buy into",  
    "downplay", "cast doubt on", "shrug off", "badmouth", "refute",  
    "dismiss as invalid", "challenge", "snub", "boycott actively", "scoff at",  
    "disregard completely", "deny legitimacy to", "doubt the credibility of", "be critical of", "show contempt for"
]

def consistency_of_opinion(text, positive_opinion, negative_opinion, similarity_threshold=80):
    positive_count = 0
    negative_count = 0

    for keyword in positive_opinion:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            positive_count += 1

    for keyword in negative_opinion:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            negative_count += 1

    total_count = positive_count + negative_count
    
    if total_count == 0:
        consistency = "Neutral or no opinions detected (no significant positive or negative opinions)"
    elif positive_count > 0 and negative_count > 0:
        positive_ratio = positive_count / total_count
        negative_ratio = negative_count / total_count
        
        if 0.4 <= positive_ratio <= 0.6:
            consistency = "Mixed opinions detected (balanced views with conflicting perspectives)"
        elif positive_ratio > 0.6:
            consistency = "Consistent opinions detected (majority positive views)"
        else:
            consistency = "Consistent opinions detected (majority negative views)"
    elif positive_count > 0:
        consistency = "Consistent opinions detected (only positive views)"
    else:
        consistency = "Consistent opinions detected (only negative views)"
    
    result = {
        "Positive Opinions": positive_count,
        "Negative Opinions": negative_count,
        "Total Opinions": total_count,
        "Consistency": consistency,
    }
    return result

engagement_keywords = [
    "yes", "okay", "thanks", "sure", "got it", "understood", "right", "exactly", "welcome",  
    "of course", "absolutely", "definitely", "no problem", "you're welcome", "alright", "fine",  
    "sounds good", "makes sense", "roger that", "copy that", "affirmative", "agreed", "I see",  
    "true", "correct", "that's right", "I understand", "clear", "noted", "I get it", "confirmed",  
    "appreciate it", "much obliged", "gladly", "all good", "gotcha", "that works", "fair enough",  
    "no worries", "cool", "nice", "appreciated", "cheers", "sure thing", "makes perfect sense",  
    "that's clear", "alright then", "right on", "precisely", "acknowledged", "got your point",  
    "I'm on it", "not a problem", "all set", "no doubt", "fully understood", "checking",  
    "noted with thanks", "all understood", "yep", "yeah", "okie dokie", "no objections",  
    "sounds about right", "can do", "totally", "for sure", "I'm with you", "message received",  
    "10-4", "hear you loud and clear", "point taken", "as you say", "well said", "that's the idea",  
    "you're spot on", "I acknowledge", "exactly my thought", "with you on that", "I accept",  
    "much appreciated", "great", "super", "I resonate with that", "in agreement", "makes total sense",  
    "that's fair", "we're on the same page", "I hear you", "I follow", "understood completely",  
    "no confusion", "you got it", "crystal clear", "grasped", "I concur", "that's a yes",  
    "I'm aligned", "yessir", "copy", "roger", "affirmed", "yes indeed", "I go along with that",  
    "nothing to add", "noted and agreed", "solid", "golden", "it's a deal", "with pleasure",  
    "totally on board", "consider it done", "on the same wavelength", "right you are", "checked",  
    "I can work with that", "we're good", "I appreciate that", "yup", "certainly", "by all means",  
    "fully noted", "absolutely correct", "no arguments here", "agreed 100%", "without a doubt",  
    "all noted", "full agreement", "sounds reasonable", "I dig it", "that's affirmative",  
    "say no more", "spot on", "hit the nail on the head"
]

clarifying_keywords = [
    "can you explain", "what do you mean", "could you clarify", "why", "how", "could you elaborate",  
    "what", "when", "where", "who", "which", "how does that work", "what's the reason",  
    "could you give an example", "what's the difference", "can you simplify", "can you break it down",  
    "could you rephrase that", "what exactly do you mean", "how so", "why is that",  
    "can you expand on that", "can you walk me through it", "what makes you say that",  
    "could you provide more details", "what's your reasoning", "how does this apply",  
    "can you spell it out", "what are the implications", "how is that possible", "what should I know",  
    "can you define that", "how do you figure", "what's the logic behind that",  
    "could you be more specific", "what's an example of that", "how does that relate",  
    "can you illustrate that", "how would that work", "can you elaborate further",  
    "what are the key points", "what do you mean exactly", "could you break it down further",  
    "what's the significance of that", "how does that connect", "why is this important",  
    "can you clarify the context", "can you put that in simpler terms", "what does that entail",  
    "can you run that by me again", "what are you referring to", "could you re-explain that",  
    "what's your perspective on that", "how does it function", "why does that happen",  
    "can you outline the process", "what steps are involved", "how does it differ from",  
    "can you explain it in layman's terms", "what is the background on this",  
    "how does this affect things", "what are the consequences", "how do I interpret that",  
    "could you clarify your position", "what are you implying", "how would you describe it",  
    "can you illustrate with an analogy", "what's the takeaway from that",  
    "how do you justify that", "what assumptions are being made",  
    "what does that suggest", "what do I need to understand", "why should I care about this",  
    "how does that fit into the bigger picture", "can you contrast that with something else",  
    "how do you arrive at that conclusion", "what makes this relevant",  
    "why is this the case", "can you go into more depth", "what's the underlying principle",  
    "what does that indicate", "why does this matter", "what's the fundamental idea",  
    "how do I make sense of this", "can you clarify the reasoning", "why is it structured this way",  
    "can you summarize the key points", "how do we know this is true", "what's the supporting evidence",  
    "what exactly is happening here", "can you walk me through your thought process",  
    "how does this contribute to the topic", "can you simplify your explanation",  
    "could you give a different perspective", "how can I better understand this",  
    "what is your interpretation", "how does this fit into the framework",  
    "can you explain from a different angle", "what are the missing details",  
    "what would be an alternative explanation", "how do I approach this concept",  
    "can you define it more precisely", "what's the relevance of this",  
    "could you clarify with a practical example", "what's the key takeaway",  
    "what's another way to look at it", "how can I apply this knowledge",  
    "what's the best way to understand this", "can you describe it differently"
]

def alertness_in_conversation(text, engagement_keywords, clarifying_keywords, similarity_threshold=80):
    engagement_count = 0
    clarifying_count = 0

    for keyword in engagement_keywords:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            engagement_count += 1

    for keyword in clarifying_keywords:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            clarifying_count += 1

    total_alertness_words = engagement_count + clarifying_count
    total_words = len(text.split())

    if total_alertness_words == 0:
        return {
            "Message": "No engagement detected",
            "Engagement Words": 0,
            "Clarifying Words": 0,
            "Total Words": total_words,
            "Alertness Level": "Unengaged conversation detected"
        }

    engagement_ratio = engagement_count / total_alertness_words
    clarifying_ratio = clarifying_count / total_alertness_words

    if engagement_ratio > 0.7:
        alertness_level = "Highly engaged and attentive"
    elif clarifying_ratio > 0.7:
        alertness_level = "Clarification-focused conversation detected"
    elif 0.4 <= engagement_ratio <= 0.6:
        alertness_level = "Balanced engagement and clarification detected"
    else:
        alertness_level = "Slightly responsive conversation"

    balance_difference = abs(engagement_ratio - clarifying_ratio)

    if balance_difference < 0.2 and total_alertness_words > 10:
        alertness_level = "Dynamic and balanced engagement detected"
    elif balance_difference < 0.1:
        alertness_level = "Highly balanced engagement detected"

    result = {
        "Engagement Words": engagement_count,
        "Clarifying Words": clarifying_count,
        "Total Alertness Words": total_alertness_words,
        "Total Words": total_words,
        "Engagement Ratio": round(engagement_ratio, 2),
        "Clarifying Ratio": round(clarifying_ratio, 2),
        "Balance Difference": round(balance_difference, 2),
        "Alertness Level": alertness_level,
    }
    return result



friendly_keywords = [
    "great", "amazing", "fantastic", "wonderful", "impressive", "outstanding", "excellent", 
    "superb", "brilliant", "remarkable", "awesome", "terrific", "spectacular", "phenomenal",
    "keep it up", "well done", "good job", "nicely done", "hats off", "kudos", "you're doing great",
    "proud of you", "exceptional work", "stellar", "commendable", "marvelous",
    "thank you", "appreciate", "grateful", "much obliged", "many thanks", "deeply appreciate",
    "sincerely grateful", "heartfelt thanks", "big thanks", "immensely thankful",
    "nice", "lovely", "charming", "delightful", "cheerful", "joyful", "heartwarming", "pleasing",
    "bright", "uplifting", "positive", "sunny", "welcoming", "kind",
    "exciting", "thrilled", "stoked", "ecstatic", "elated", "eager", "enthusiastic", "pumped",
    "overjoyed", "beyond excited", "buzzing", "hyped",
    "you're right", "absolutely", "totally agree", "I support that", "you're on point", 
    "good call", "sounds perfect", "well put", "wise words", "insightful", "spot on",
    "you're amazing", "you're incredible", "so talented", "gifted", "brilliant mind", 
    "creative genius", "genius-level", "a real pro", "exceptionally skilled", "inspirational", 
    "love it", "this is fantastic", "can't get enough of this", "this is gold", "pure brilliance", 
    "such a treat", "pure joy", "what a delight", "truly a masterpiece",
    "I couldn't agree more", "exactly", "right on point", "so true", "couldn't have said it better",
    "100 percent agree", "absolutely spot on", "nailed it"
]

authoritative_keywords = [
    "must", "should", "have to", "need to", "ought to", "it is required", "it is necessary",
    "compulsory", "obligatory", "you are expected to", "it is crucial", "imperative",
    "justify", "explain", "prove", "demonstrate", "validate", "substantiate", "provide evidence",
    "back up", "give a rationale", "support with facts", "show cause", "make the case",
    "mandatory", "essential", "enforce", "compliance", "strictly required", "follow regulations",
    "governed by", "subject to rules", "bound by law", "must adhere to", "policy dictates",
    "guidelines require", "protocol states", "in accordance with", "stipulated by",
    "ensure", "confirm", "make sure", "verify", "guarantee", "establish", "follow instructions",
    "comply with", "adhere to", "maintain standards", "observe", "execute properly", 
    "strict adherence", "procedural requirement",
    "there is no alternative", "this is non-negotiable", "it is final", "no exceptions",
    "failure to comply", "not up for discussion", "firm decision", "without deviation",
    "directive", "mandate", "official order", "command", "edict", "decree", "executive decision",
    "dictate", "requirement", "lawful obligation", "set in stone", "binding decision",
    "failure to", "consequences include", "liable for", "breach of", "subject to penalties",
    "non-compliance results in", "strictly enforced", "violating the rules", "serious repercussions",
    "accountability lies with", "enforcement measures will be taken"
]

neutral_keywords = [
    "can you", "could you", "please", "would you", "may I ask", "I would like to know",
    "I am curious about", "do you mind", "if possible", "let me know", "seeking clarification",
    "elaborate", "describe", "explain", "detail", "clarify", "could you expand", 
    "break it down", "walk me through", "give an overview", "simplify", "outline",
    "help me understand", "could you go over", "what do you mean by",
    "what is", "how does", "who is", "where is", "when did", "why is", "which one", "define",
    "what happens if", "can you define", "what does it mean", "how would you describe",
    "what are the key points", "what is the significance", "what is the purpose",
    "tell me more", "I'd like to know more", "could you share details", "what are the details",
    "expand on that", "could you provide context", "give me more insight", "I'm looking for details",
    "break it down for me", "provide further information", "in what way", "how so",
    "suppose", "let's assume", "consider the case where", "hypothetically speaking",
    "imagine if", "what if", "how would things change if", "in a scenario where",
    "how does this compare to", "what are the differences", "what are the similarities",
    "how does it relate to", "what's the impact of", "what are the advantages",
    "what are the disadvantages", "how does it affect", "is there an alternative",
    "let's discuss", "let's analyze", "looking at the facts", "in an objective sense",
    "from a neutral standpoint", "without bias", "without taking sides",
    "can you provide data", "what do the numbers say", "is there evidence for this",
    "do you have statistics", "what research supports this", "any references for this",
    "walk me through the process", "how do I", "what's the procedure", "what are the steps",
    "explain the methodology", "guide me through", "show me how to", "could you demonstrate",
    "can you give an example", "what's a real-world example", "can you illustrate",
    "what's a case study", "any historical examples", "could you show a practical case"
]

open_ended_keywords = [
    "how", "what", "why", "explain", "describe", "tell me about", "elaborate on",  
    "can you clarify", "give an overview of", "provide insights on", "define",  
    "illustrate", "what are the reasons for", "how does", "what makes",  
    "what are the differences between", "in what ways", "explore",  
    "what happens when", "walk me through", "how can one", "what are some",  
    "what is the impact of", "analyze", "discuss", "shed light on", "interpret",  
    "break down", "summarize", "why is it important", "how do you",  
    "how does one", "why do people", "what do you think about",  
    "what factors contribute to", "what is the significance of",  
    "what role does", "compare and contrast", "what are the benefits of",  
    "how does this work", "how can we improve", "how would you",  
    "how do scientists", "how has this changed", "how do experts",  
    "examine", "what is the history of", "how does it relate to",  
    "what strategies can be used", "what are the characteristics of",  
    "what methods are available", "what techniques exist",  
    "what does it mean to", "what are the key concepts in",  
    "what challenges arise in", "what solutions exist for",  
    "what does research say about", "how can it be applied",  
    "how do different cultures view", "what ethical considerations are involved",  
    "what is the process of", "how is it structured",  
    "how does technology influence", "what are the underlying principles of",  
    "what are the scientific explanations for", "what are the historical perspectives on",  
    "what role does innovation play in", "how do policies affect",  
    "what are the limitations of", "how can we address", "what does the future hold for",  
    "how does globalization impact", "what perspectives exist on",  
    "what social factors influence", "how do emotions affect",  
    "what psychological factors contribute to", "what philosophical questions arise from",  
    "what are the artistic interpretations of", "how is it portrayed in media",  
    "what are the real-world applications of", "how do economic factors play a role in",  
    "what scientific studies support", "what are the environmental implications of",  
    "what legal frameworks govern", "how has it evolved over time",  
    "how do experts predict", "what do surveys reveal about",  
    "what cultural traditions surround", "what are the demographic patterns of",  
    "what are the best practices for", "how do professionals approach",  
    "what lessons can be learned from", "how do different industries use",  
    "what are the trade-offs involved in", "what does data reveal about",  
    "what case studies exist on", "what are the moral dilemmas in",  
    "how do we measure success in", "what role do emotions play in",  
    "what are the ethical implications of", "what frameworks exist for",  
    "what psychological theories explain", "how does perception influence",  
    "what are the risks associated with", "how do biases impact",  
    "what skills are required for", "what research methodologies are used in",  
    "how does culture shape", "what global trends affect",  
    "how do experts define", "what are the leading theories in",  
    "how does policy impact", "what common misconceptions exist about",  
    "how do social movements influence", "what are the root causes of",  
    "how do historical events shape", "what are the latest findings on",  
    "how can we foster", "what are the barriers to",  
    "how do technological advances affect", "what breakthroughs have occurred in",  
    "what societal impacts result from", "how do we navigate challenges in",  
    "what are the underlying assumptions of", "how do different perspectives approach",  
    "how do we interpret data on", "how do human behaviors shape",  
    "how do educational systems address", "what are the foundational concepts in",  
    "what advancements are being made in", "how can collaboration enhance",  
    "how do economic disparities affect", "what role does ethics play in",  
    "how do trends in society shape", "what impact does government policy have on",  
    "what best explains", "how can interdisciplinary approaches help in",  
    "what are the core ideas behind", "what are the broader implications of",  
    "what lessons does history teach about", "how does human behavior influence",  
    "how can we evaluate the success of", "what factors determine",  
    "how do social networks impact", "how do experts analyze",  
    "what are the cutting-edge developments in", "how can innovation drive",  
    "what are the historical roots of", "how does urbanization affect",  
    "what future challenges might arise in", "how do different age groups perceive",  
    "what new discoveries are emerging in", "what challenges do policymakers face in",  
    "how can we optimize", "how does education influence",  
    "how do trends evolve in", "what are the psychological impacts of",  
    "what perspectives do scholars offer on", "what solutions are being proposed for",  
    "what industries are most affected by", "how can ethical considerations guide",  
    "how do organizations manage", "how do different fields intersect in",  
    "what are the latest policy changes in", "how does literature reflect",  
    "how do values shape", "what controversies surround",  
    "how do ecosystems respond to", "how does infrastructure affect",  
    "how can leaders influence", "how does social media shape",  
    "what are the emerging patterns in", "how does art represent",  
    "how can individuals contribute to", "how does technology mediate",  
    "what debates exist about", "how do institutions regulate",  
    "what innovative solutions are being developed for", "how does globalization challenge",  
    "how do narratives shape", "how can resilience be built in",  
    "how do we quantify", "what are the psychological mechanisms behind",  
    "how does the brain process", "what mechanisms drive",  
    "how does adaptation occur in", "how do incentives affect",  
    "how do digital tools enhance", "how do we frame",  
    "what paradoxes exist in", "what does an interdisciplinary approach reveal about"  
]

follow_up_phrases = [
    "can you elaborate", "could you clarify", "can you explain more",  
    "tell me more", "could you expand on that", "could you go into more detail",  
    "what do you mean by that", "could you provide an example",  
    "how does that work", "can you break it down further",  
    "why is that the case", "could you simplify it", "can you give me a deeper insight",  
    "could you illustrate that with an example", "what makes that important",  
    "how does it relate to", "what are the key takeaways",  
    "can you summarize that in a different way", "can you provide additional context",  
    "what are the implications of that", "how does it compare to",  
    "why is that relevant", "can you make it clearer", "could you rephrase that",  
    "can you give me a different perspective", "can you provide a real-world example",  
    "how does that affect the bigger picture", "why is that significant",  
    "what are the possible consequences", "what led to that",  
    "what's the reasoning behind that", "can you put that in simpler terms",  
    "how does that connect to what we discussed earlier",  
    "can you walk me through it step by step", "can you highlight the key points",  
    "what are the main factors involved", "how would you describe that in layman's terms",  
    "what are the supporting arguments for that", "can you give more background on this",  
    "how does that influence other things", "can you give a different angle on this",  
    "how do experts interpret this", "can you explain this from a different perspective",  
    "what's the historical context behind this", "could you go a bit further into that",  
    "how does that impact the current situation", "what challenges does this present",  
    "how does this tie into the bigger picture", "can you go into the nuances of this",  
    "how would this be applied in practice", "what are some common misconceptions about this",  
    "what would be an alternative viewpoint", "what's a good analogy for this",  
    "can you make this easier to understand", "what makes this stand out",  
    "how does this affect people on a daily basis", "what are the broader consequences",  
    "what's the most important aspect of this", "could you break that down into smaller parts",  
    "can you provide an analogy", "can you expand on the logic behind that",  
    "what assumptions are being made here", "how did this concept evolve over time",  
    "how does this compare with similar ideas", "what are the key debates around this",  
    "what does the latest research say about this", "how would you contrast this with another idea",  
    "what's the practical application of this", "how would you explain this to a beginner",  
    "what do critics say about this", "how do different people interpret this",  
    "what historical events are linked to this", "can you explore this idea in more depth",  
    "what are the ethical considerations here", "what perspectives are missing from this discussion",  
    "how does this play out in different industries", "how does culture influence this",  
    "what are the foundational principles behind this", "what role does science play in this",  
    "what are the unanswered questions about this", "what theories support this concept",  
    "how does this connect with trends in the field", "what's the controversy surrounding this",  
    "can you provide some real-life case studies", "what's the step-by-step process for this",  
    "how do professionals handle this", "what are some counterarguments to this",  
    "how does this align with best practices", "what are the biggest knowledge gaps here",  
    "how does this vary across different regions", "what does data tell us about this",  
    "how do scholars approach this issue", "can you connect this with another key idea",  
    "how does public opinion influence this", "what are the major developments in this area",  
    "how do regulations impact this", "what are some unexpected insights about this",  
    "what are the risks associated with this", "how do different industries handle this",  
    "what recent discoveries have been made in this field", "how does this play into global trends",  
    "what future implications might arise from this", "how does this affect individuals versus society",  
    "how has this changed over time", "what alternative perspectives exist on this",  
    "what role does innovation play in this", "how does funding influence this field",  
    "what are the foundational texts on this subject", "what factors shape public perception of this",  
    "how does this relate to economic factors", "how does this challenge existing knowledge",  
    "what are the technical aspects of this", "how do different philosophies approach this",  
    "what makes this concept controversial", "how do emotions shape our understanding of this",  
    "what are the limitations of current thinking on this", "what surprising connections exist with other fields",  
    "how do different methodologies approach this", "what role does technology play in this",  
    "how do various cultures understand this differently", "what's the role of personal experience in this",  
    "how can this be tested or measured", "what data sources support this",  
    "how do institutions shape the conversation on this", "what lessons can be drawn from historical examples",  
    "how does this affect different social groups", "how does this shape policy-making",  
    "what practical strategies can be derived from this", "what is the biggest misconception about this",  
    "how does this field intersect with other disciplines", "what are the next big questions to explore in this area",  
    "what are the counterpoints to this argument", "what are the strongest arguments in favor of this",  
    "how do biases influence interpretations of this", "how does storytelling impact understanding of this topic",  
    "what examples challenge conventional wisdom on this", "how do different generations view this",  
    "how can we evaluate success in this area", "what surprising outcomes have emerged from this",  
    "how does this idea manifest in pop culture", "how does this affect decision-making",  
    "how does the media portray this issue", "how does humor play a role in discussing this",  
    "how does this impact personal identity", "what does neuroscience reveal about this",  
    "how does misinformation affect perceptions of this", "what analogies best illustrate this concept",  
    "how do historical patterns help us predict the future of this", "how does trust impact the adoption of this idea",  
    "what strategies help in understanding this better", "what's the most counterintuitive insight about this",  
    "how does this relate to the psychology of learning", "how does curiosity shape engagement with this topic",  
    "how does uncertainty play a role in this", "what aspects of this are still debated today",  
    "how can this be simplified without losing its essence", "how can storytelling enhance understanding of this",  
    "how can this knowledge be applied in everyday life", "how do different economic systems affect this",  
    "what role does language play in shaping perceptions of this", "what alternative models exist for understanding this",  
    "how does urban planning relate to this", "how does this connect to personal responsibility",  
    "how does this factor into ethical decision-making", "how does access to information shape views on this",  
    "how do scientific advancements change our understanding of this", "how does power influence narratives about this"  
]

active_listening_phrases = [
    "I see", "That's interesting", "Go on", "I understand", "That makes sense",  
    "Oh, I get it now", "I hear you", "Got it", "I see what you mean",  
    "That's a good point", "I follow you", "That's fascinating",  
    "Please continue", "Tell me more", "I appreciate that",  
    "I hadn't thought about it that way", "That's a fresh perspective",  
    "I see where you're coming from", "That's a compelling argument",  
    "That's an important insight", "I'm with you on that", "That resonates with me",  
    "You make a strong point", "That clarifies things",  
    "Thanks for sharing that", "That's a great observation",  
    "That's quite thought-provoking", "I can see how that would be the case",  
    "I hadn't considered that before", "That's a unique way to look at it",  
    "Now that you mention it, that makes sense",  
    "I completely understand your point of view", "That sheds some light on it",  
    "That helps clarify things", "I appreciate your perspective",  
    "That's a key insight", "I can relate to that", "That's a valid point",  
    "I see how that connects", "That's something worth considering",  
    "I never thought about it that way", "You bring up an important point",  
    "That aligns with what I've heard before",  
    "That's a strong argument", "That fits into the bigger picture",  
    "That's an intriguing perspective", "That's a powerful way to put it",  
    "I hadn't looked at it like that", "That's a fair point",  
    "That's an insightful observation", "You've given me something to think about",  
    "That's a great way to put it", "That's an interesting angle",  
    "That really puts things in perspective",  
    "That's an important distinction", "I get what you're saying",  
    "That's an insightful take on it", "I see your logic",  
    "I appreciate your thought process", "That definitely adds up",  
    "I can understand why you'd think that", "That's worth reflecting on",  
    "That's a crucial factor", "That's quite eye-opening",  
    "That's a perspective I hadn't considered", "That's a very logical point",  
    "That's a fresh take on it", "That really clarifies things",  
    "I'm intrigued by that perspective", "That highlights an important issue",  
    "That's a very nuanced view", "That's something to keep in mind",  
    "I hadn't connected those ideas before", "That's very perceptive",  
    "That's an essential aspect", "That's an excellent observation",  
    "That really stands out", "That's a significant point",  
    "That brings a new perspective to the discussion",  
    "That makes me think differently about it",  
    "That's a helpful way to frame it", "That's definitely something to consider",  
    "That's an important aspect to highlight",  
    "That connects well with what we've been discussing",  
    "That provides a clearer picture", "That really puts things in context",  
    "That's a profound insight", "That's a well-articulated thought",  
    "That connects a lot of dots", "That's a strong insight",  
    "I can definitely see why that's important",  
    "That reinforces an important point", "That's an elegant way to express it",  
    "That's a well-thought-out perspective", "That adds depth to the discussion",  
    "That gives me a new way to think about it", "That's an eye-opening connection",  
    "That helps put things into perspective", "That's a crucial insight",  
    "That's a significant contribution to the discussion",  
    "That's an idea worth exploring further",  
    "That's a logical way to look at it", "That really expands my understanding",  
    "That challenges a common assumption", "That's a key piece of the puzzle",  
    "That's a refreshing take", "That makes the concept much clearer",  
    "That's an intriguing way to explain it", "That really brings clarity",  
    "That ties in beautifully with our discussion", "That's a well-structured thought",  
    "That connects with a lot of what I've been thinking",  
    "That's a particularly insightful way to phrase it",  
    "That adds a layer of depth", "That's a sharp observation",  
    "That puts a lot of things into perspective",  
    "That's a great way to synthesize the idea",  
    "That really encapsulates the issue",  
    "That gives a richer understanding", "That's a thought-provoking point",  
    "That's a fundamental aspect of the topic",  
    "That really underlines an important issue",  
    "That's an original perspective", "That's a well-reasoned analysis",  
    "That's a vital consideration", "That fits well with what I've seen before",  
    "That adds a new dimension", "That's a compelling way to look at it",  
    "That's a useful distinction", "That highlights a critical issue",  
    "That's an interesting way to frame it", "That's a striking observation",  
    "That opens up new possibilities", "That's a smart way to interpret it",  
    "That shifts the way I see it", "That's a creative way to express it",  
    "That gives a lot to think about", "That highlights a key issue",  
    "That presents a fresh way to analyze it",  
    "That's an insightful way to approach it",  
    "That broadens the discussion in a meaningful way",  
    "That's an aspect I hadn't thought of before",  
    "That's an excellent way to capture it",  
    "That's an essential takeaway", "That introduces a new way to think about it",  
    "That brings an important nuance to the conversation",  
    "That makes the argument even stronger",  
    "That's an important piece of the puzzle",  
    "That brings an unexpected but valuable perspective",  
    "That ties together a lot of concepts",  
    "That's a significant way to frame the issue",  
    "That articulates the idea beautifully",  
    "That's a noteworthy insight", "That resonates deeply",  
    "That's a powerful point", "That contributes a lot to the conversation",  
    "That helps ground the discussion", "That really shifts my perspective",  
    "That's a perspective I hadn't fully appreciated before",  
    "That's an elegant way to explain it",  
    "That really refines the argument", "That brings an important clarity",  
    "That perfectly sums it up", "That's a critical distinction",  
    "That's an insightful conclusion", "That's a fresh way to approach it",  
    "That makes a lot of sense in this context",  
    "That's an observation that deserves more attention",  
    "That really helps frame the conversation",  
    "That's an unexpected but crucial perspective",  
    "That deepens my understanding of the issue",  
    "That's a key insight into the topic"  
]

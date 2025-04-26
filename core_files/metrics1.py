from rapidfuzz import process, fuzz

sarcasm_indicators = [
    "oh great", "sure thing", "totally", "yeah right", "as if", "of course",  
    "good for you", "brilliant", "nice job", "fantastic", "impressive", "just perfect",  
    "oh wonderful", "amazing", "really?", "wow, incredible", "yeah, that's exactly what I needed",  
    "as expected", "sure, whatever", "oh, that's lovely", "nice going", "just what I needed",  
    "oh wow", "how original", "genius", "so helpful", "that's just amazing", "what a surprise",  
    "oh, isn't that special", "because that makes sense", "yeah, no kidding", "what a brilliant idea",  
    "oh, how convenient", "I totally believe you", "just fantastic", "oh, I love that",  
    "of course that happened", "obviously", "oh, what a great plan", "just awesome",  
    "sure, why not", "I couldn't be happier", "that's the best news ever", "oh, absolutely",  
    "yes, because that always works", "how lucky", "wow, you're so smart", "oh, please",  
    "just my luck", "because that's logical", "what a genius move", "oh sure, that's totally fair",  
    "that's exactly what I was hoping for", "oh, how delightful", "fantastic, just fantastic",  
    "oh, what a joy", "can't wait", "love that for me", "so thrilled", "this is just great",  
    "oh yes, my favorite thing", "well, isn't that just perfect", "what a dream",  
    "wow, what an incredible opportunity", "so unexpected, who would've thought",  
    "oh good, just what I always wanted", "lucky me", "what a time to be alive",  
    "oh joy", "I'm overwhelmed with excitement", "how exciting", "how generous",  
    "what a brilliant idea, truly", "I'm absolutely amazed", "well, isn't that just peachy",  
    "unbelievable… in the worst way", "oh sure, because that makes total sense",  
    "wow, that's so innovative", "just my favorite thing ever", "oh yes, I was hoping for that",  
    "amazing, just amazing", "how fortunate", "I feel so lucky right now",  
    "sure, because that's exactly how things work", "wow, just wow", "absolutely genius",  
    "fascinating, tell me more", "how predictable", "well, that's just the cherry on top",  
    "no way, I'm so impressed", "oh wow, you don't say", "gee, thanks",  
    "because that's totally what I meant", "oh, I live for moments like this",  
    "oh wow, let me write that down", "so glad I asked", "truly inspiring",  
    "sure, go ahead, ruin my day", "this is going exactly how I planned",  
    "wow, such a groundbreaking revelation", "yes, that is precisely what I wanted",  
    "oh yes, that's exactly how it should be", "oh no, I totally believe you",  
    "how about no", "oh wow, I never would have guessed",  
    "yes, because that's how reality works", "well, isn't that just fantastic",
    "oh, that's exactly what I needed right now", "oh sure, I have nothing better to do",  
    "what a fantastic idea, truly inspiring", "so grateful for this",  
    "this is exactly how I wanted my day to go", "yes, I love wasting my time",  
    "how unexpected, truly shocking", "well, that went just as planned",  
    "oh yes, I was just thinking the same thing", "because that's totally fair",
    "yes, because I love problems", "wow, never saw that coming",  
    "so glad this happened", "oh wow, I'll be sure to take notes",  
    "how lucky am I", "oh, how fun", "so glad I get to experience this",  
    "can't imagine anything better", "how about that, what a coincidence",  
    "oh sure, let's add more to the mess", "oh, how insightful",  
    "well, that just made my day", "wow, I'm blown away",  
    "I am absolutely loving this", "just what I needed today",  
    "yes, because this is exactly how I imagined my life",  
    "I'm sure this will turn out great", "how fortunate for me",  
    "oh, you're so right, I should've known",  
    "oh yes, I love dealing with this", "yes, because I have all the time in the world",  
    "wow, what a flawless idea", "oh, this is just getting better and better",  
    "truly, a moment to cherish", "I wouldn't have it any other way",  
    "how original and groundbreaking", "just wonderful, I couldn't be happier",  
    "oh, that's so interesting, tell me more", "yes, because nothing could go wrong",  
    "oh wow, how revolutionary", "what a stroke of genius", "truly a blessing",  
    "I can't believe how lucky I am", "how fortunate that this happened",  
    "what a pleasant surprise", "oh, this is exactly what I needed in my life",  
    "I can't believe my good fortune", "oh yes, let's do that, why not",  
    "truly a masterpiece of an idea", "wow, that's a fresh take",  
    "oh, I totally saw that coming", "this is going to be amazing, I'm sure of it"
]

exaggeration_phrases = [
    "never in a million years", "the best ever", "so amazing", "unbelievable", "couldn't be better",  
    "absolutely perfect", "over the moon", "world's greatest", "once in a lifetime",  
    "hands down the best", "totally awesome", "unmatched", "the greatest thing ever",  
    "beyond belief", "insanely good", "unreal", "too good to be true", "without a doubt the best",  
    "out of this world", "beyond imagination", "mind-blowing", "off the charts", "pure perfection",  
    "legendary", "nothing comes close", "the pinnacle of greatness", "a dream come true",  
    "light-years ahead", "the peak of excellence", "unquestionably the best",  
    "spectacular beyond words", "next-level amazing", "absolutely phenomenal",  
    "the most incredible thing ever", "by far the best", "history in the making",  
    "a once-in-a-generation event", "epic in every way", "more than extraordinary",  
    "as good as it gets", "the ultimate experience", "jaw-droppingly amazing",  
    "the definition of perfection", "like nothing else in the world", "too good for words",  
    "so incredible it's hard to believe", "without comparison", "completely mind-blowing",  
    "utterly fantastic", "on a whole different level", "the absolute peak",  
    "words can't describe how amazing this is", "the most spectacular thing ever",  
    "perfection at its finest", "something out of a movie", "beyond legendary",  
    "nothing short of miraculous", "the gold standard", "impossibly good",  
    "beyond all expectations", "so good it's almost unfair", "the best thing since sliced bread",  
    "nothing has ever come close", "beyond comprehension", "a life-changing experience",  
    "so good it defies logic", "hard to believe how amazing this is", "pure magic",  
    "the eighth wonder of the world", "a miracle in itself", "an absolute masterpiece",  
    "so flawless it must be a dream", "too good to be real", "so amazing it's almost supernatural",  
    "this changes everything", "more perfect than perfect", "as if touched by the gods",  
    "beyond words", "so good it's scary", "a groundbreaking achievement",  
    "the most mind-boggling thing ever", "earth-shatteringly good",  
    "as if the universe conspired for this to happen", "so rare it's priceless",  
    "the single most important thing ever", "the best thing humanity has ever created",  
    "the ultimate game-changer", "it doesn't get better than this",  
    "so outstanding it breaks all records", "the highlight of my entire life",  
    "monumentally incredible", "in a league of its own", "on a whole new dimension",  
    "like winning the cosmic lottery", "so perfect it's almost divine",  
    "beyond the limits of human achievement", "so stunning it redefines beauty",  
    "the most remarkable thing to ever exist", "as if reality itself was improved",  
    "so flawless it should be illegal", "so astonishing it's almost supernatural",  
    "an era-defining event", "a spectacle for the ages", "something out of a fantasy",  
    "so exhilarating it's beyond thrilling", "so perfect it feels unreal",  
    "a marvel of human creativity", "an explosion of perfection",  
    "more thrilling than any adventure ever told", "so extraordinary it rewrites history",  
    "an experience like no other", "so unique it's impossible to describe",  
    "as rare as a unicorn", "like finding treasure in your backyard",  
    "the most beautiful sight known to humankind", "so powerful it shakes the heavens",  
    "awe-inspiring beyond compare", "more satisfying than anything imaginable",  
    "a defining moment in history", "so delightful it melts the soul",  
    "more entertaining than the greatest show on Earth",  
    "the most mesmerizing thing ever created", "so astonishing it bends reality",  
    "on a level beyond human comprehension", "so breathtaking it steals the air from your lungs",  
    "more incredible than any legend", "the most legendary event of our time",  
    "so astonishing it's almost divine intervention", "as groundbreaking as the discovery of fire",  
    "the kind of moment that changes the course of destiny",  
    "so thrilling it makes every other excitement seem dull",  
    "the most unreal thing to ever happen", "a phenomenon beyond imagination",  
    "like discovering a whole new universe", "so stunning it's a once-in-eternity event"
]

contradictory_phrases = [
    "but", "however", "on the contrary", "yet", "although", "despite", "in contrast", 
    "nevertheless", "nonetheless", "contradictory", "ironically", "on the other hand", 
    "even though", "still", "though", "despite that", "whereas", "instead", "regardless", 
    "opposite", "except", "though", "in spite of", "counter to", "contrary to", 
    "all the same", "for all that", "notwithstanding", "on the flip side", "then again", 
    "in reverse", "in contradiction", "unlike", "inverse", "against", "though still", 
    "even so", "but then", "differently", "disagreeing with", "counter to", "just the opposite", 
    "not quite", "inconsistently", "although still", "regardless of", "this, however", 
    "however, that's not the case", "in stark contrast", "unlike what was expected", 
    "the opposite is true", "against all odds", "unexpectedly", "not what you'd think", 
    "opposed to", "completely different", "counteracting", "paradoxically", "conversely", 
    "neither here nor there", "irreconcilable", "can't be both", "on the other side", 
    "something else entirely", "defies logic", "disproving", "flipping the script", 
    "a different story", "this doesn't match", "the reverse is true", "an antithesis", 
    "a contradiction in terms", "diametrically opposed", "more likely the opposite", 
    "opposing viewpoint", "not the case", "out of place", "offbeat", "incongruous", 
    "doesn't line up", "out of sync", "counterargument", "clashing", "incongruent", 
    "incompatible", "irrelevant", "conflicting", "irrelevant to", "a paradox", 
    "mutually exclusive", "disconnected", "off-track", "divergent", "a twist", 
    "undermining", "totally different", "unexpected contradiction", "a paradoxical situation", 
    "inconsistent", "counterintuitive", "incongruous with", "something doesn't add up", 
    "it's not that simple", "more complicated than that", "unexpectedly contradictory", 
    "quite the opposite", "it doesn't fit", "completely misaligned", "out of step", 
    "completely incompatible", "doesn't follow", "not quite what you thought", 
    "nothing to do with", "counterproductive", "discrepant", "completely against", 
    "non-conformist", "deviates", "strangely contradictory", "in opposition to", 
    "doesn't match", "in conflict", "something doesn't make sense", "not as it seems", 
    "not the same thing", "incoherent", "opposing", "anomaly", "distorted", 
    "unsynchronized", "nothing like expected", "off-kilter", "out of alignment", 
    "different from what was suggested", "doesn't follow the pattern", "disturbingly opposite", 
    "contrasting", "unbalanced", "an opposing viewpoint", "a different direction", 
    "an alternate reality", "to the contrary", "defies expectation", "a contradiction", 
    "doesn't match reality", "this doesn't add up", "unpredictable", "incompatible with", 
    "mismatched", "unlike what was anticipated", "throws off the balance", "out of character", 
    "disproves the point", "against the grain", "totally different perspective", 
    "off the mark", "a mismatch", "no alignment", "this doesn't make sense", 
    "something's wrong", "the reality is different", "throws everything off", "totally contradictory", 
    "doesn't add up", "a distorted view", "out of the ordinary", "just doesn't fit"
]

def detect_sarcasm(text, sarcasm_indicators, exaggeration_phrases, contradictory_phrases, similarity_threshold=80):
    sarcasm_count = 0
    exaggeration_count = 0
    contradiction_count = 0

    for keyword in sarcasm_indicators:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            sarcasm_count += 1

    for keyword in exaggeration_phrases:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            exaggeration_count += 1

    for keyword in contradictory_phrases:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            contradiction_count += 1

    total_sarcasm_signals = sarcasm_count + exaggeration_count + contradiction_count
    total_words = len(text.split())

    if total_sarcasm_signals == 0:
        return {
            "Message": "No sarcasm detected",
            "Sarcasm Indicators": 0,
            "Exaggerations": 0,
            "Contradictions": 0,
            "Total Words": total_words,
            "Sarcasm Level": "Neutral"
        }

    sarcasm_ratio = sarcasm_count / total_sarcasm_signals
    exaggeration_ratio = exaggeration_count / total_sarcasm_signals
    contradiction_ratio = contradiction_count / total_sarcasm_signals

    if sarcasm_ratio > 0.6:
        sarcasm_level = "High sarcasm detected (frequent sarcasm phrases)"
    elif exaggeration_ratio > 0.6:
        sarcasm_level = "Exaggeration-heavy sarcasm detected"
    elif contradiction_ratio > 0.6:
        sarcasm_level = "Contradiction-based sarcasm detected"
    elif total_sarcasm_signals / total_words > 0.1:
        sarcasm_level = "Moderate sarcasm detected"
    else:
        sarcasm_level = "Low sarcasm detected"

    result = {
        "Sarcasm Indicators": sarcasm_count,
        "Exaggerations": exaggeration_count,
        "Contradictions": contradiction_count,
        "Total Sarcasm Signals": total_sarcasm_signals,
        "Total Words": total_words,
        "Sarcasm Ratio": round(sarcasm_ratio, 2),
        "Exaggeration Ratio": round(exaggeration_ratio, 2),
        "Contradiction Ratio": round(contradiction_ratio, 2),
        "Sarcasm Level": sarcasm_level,
    }
    return result

high_risk_words = [
    "danger", "hazard", "threat", "peril", "unsafe", "precarious", "uncertain", 
    "risky", "vulnerable", "exposed", "jeopardy", "endanger", "dangerous", "at risk", 
    "risk factor", "potential danger", "unsafe conditions", "high stakes", "high risk", 
    "critical", "life-threatening", "fatal", "deadly", "disastrous", "catastrophic", 
    "calamitous", "hazardous", "toxic", "toxic conditions", "unpredictable", "dangerously", 
    "compromised", "in jeopardy", "grave danger", "precariously", "risky proposition", 
    "unfavorable", "unsteady", "unstable", "vulnerable situation", "fragile", "compromised safety", 
    "disruptive", "perilous", "unprotected", "under threat", "dangerous territory", "in harm's way", 
    "unreliable", "fragility", "insecure", "precarious position", "imminent danger", "volatile", 
    "unstable conditions", "a recipe for disaster", "imperiled", "risky behavior", "volatile situation", 
    "at the brink", "potential hazard", "out of control", "unforeseen danger", "at risk of", 
    "liable to", "susceptible to", "endangered", "unsafe circumstances", "troublesome", 
    "perilous situation", "danger zone", "red flag", "high-stakes gamble", "highly volatile", 
    "fragile environment", "threatening", "susceptible", "at high risk", "unpredictable outcomes", 
    "potential harm", "dangerous circumstances", "in peril", "life-threatening risks", 
    "risk of failure", "dangerous consequences", "severe risk", "critical risk", "harmful", 
    "toxic risk", "threatened", "dangerous likelihood", "imminent peril", "susceptibility", 
    "unpredictability", "imminent threat", "dangerous outcome", "uncalculated risk", 
    "defenseless", "dangerous potential", "vulnerable to", "at risk of harm", "unsecured", 
    "threatening situation", "unstable risk", "hazardous situation", "potential threat", 
    "high danger", "disruptive consequences", "dangerous proposition", "serious risk", 
    "toxic situation", "high exposure", "unreliable conditions", "significant risk", 
    "disastrous consequences", "major hazard", "unforeseen risk", "grave situation", 
    "potentially fatal", "risky proposition", "unsafe conditions", "vulnerable state", 
    "fragile condition", "dangerous impact", "imminent threat", "volatile conditions", 
    "severe danger", "at serious risk", "precarious situation", "threat of danger", 
    "highly dangerous", "vulnerable state", "risky circumstances", "risk of injury", 
    "unreliable safety", "life-risking", "catastrophic potential", "potential loss", 
    "out of control situation", "threatening environment", "unpredictable scenario", 
    "at high danger", "destructive potential", "fragile safety", "vulnerable to harm", 
    "risk of failure", "perilous circumstances", "toxic risk", "dangerous threats", 
    "volatile conditions", "hazardous environment", "at grave risk", "potential disaster", 
    "risky scenario", "dangerous exposure", "life-threatening hazards", "major risk factor", 
    "dangerous outcome", "critical vulnerability", "uncertain future", "unfavorable risk", 
    "hazardous behavior", "extreme danger", "sensitive to risks", "risk-prone", 
    "vulnerable to threats", "unprotected risk", "unmanageable danger", "volatile situation", 
    "deadly exposure", "life-threatening situation", "potential catastrophe", "unreliable outcomes", 
    "dangerous fluctuations", "exposed to danger", "high stakes risk", "unstable risk", 
    "imminent hazard", "unsafe practices", "vulnerable position", "potential loss", 
    "disastrous situation", "insecure environment", "high-threat risk", "high-risk conditions", 
    "unmanageable peril", "dire risk", "dangerous risk", "risk-filled", "critical risk factor", 
    "potentially devastating", "perilous journey", "unforeseen consequences", "deadly risk", 
    "at significant risk", "uncontrolled danger", "grave hazard", "dangerous ramifications", 
    "at a disadvantage", "hazardous potential", "high danger zone", "vulnerable state of affairs", 
    "increasing danger", "imminent risk", "at high hazard", "severe exposure", "vulnerable to attack", 
    "dangerous unknowns", "unsure outcome", "risky venture", "hazardous potential", "dangerous likelihood", 
    "uncertain path", "unfavorable outcome", "untrustworthy", "risky investment", "extreme vulnerability", 
    "fragile safety", "dangerous outcomes", "critical exposure", "unstable risk factor", "threatening danger", 
    "catastrophic scenario", "at great risk", "imminent failure", "unsafe proposition", "high-risk factor", 
    "potential threat to safety", "deadly threat", "grave danger zone", "uncontrolled situation", 
    "dangerous trajectory", "dangerous uncertainty", "vulnerable path", "high risk of loss", 
    "unsafe venture", "severe consequences", "high danger zone", "extreme hazard", "potentially catastrophic", 
    "perilous condition", "dangerous edge", "critical danger", "susceptible to damage", "seriously risky", 
    "untrustworthy environment", "high-risk zone", "unpredictable hazard", "unstable scenario", 
    "risky gamble", "unstable environment", "disastrous risk", "unprotected situation", "potential threat", 
    "dangerous gamble", "high hazard", "at the edge of danger", "extreme potential risk", 
    "dangerous condition", "at significant danger", "at perilous risk", "toxic potential", 
    "unfavorable danger", "serious peril", "imminent hazard"
]

def detect_high_risk_words(text, high_risk_words, similarity_threshold=80):
    high_risk_count = 0

    for keyword in high_risk_words:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            high_risk_count += 1

    total_words = len(text.split())

    high_risk_ratio = high_risk_count / total_words if total_words > 0 else 0

    if high_risk_count == 0:
        return {
            "Message": "No high-risk words detected",
            "High-Risk Words": 0,
            "Total Words": total_words,
            "High-Risk Ratio": round(high_risk_ratio, 2),
            "Risk Level": "Safe"
        }

    if high_risk_ratio > 0.1:
        risk_level = "High risk detected (frequent usage of high-risk words)"
    elif high_risk_ratio > 0.05:
        risk_level = "Moderate risk detected"
    else:
        risk_level = "Low risk detected"

    return {
        "High-Risk Words": high_risk_count,
        "Total Words": total_words,
        "High-Risk Ratio": round(high_risk_ratio, 2),
        "Risk Level": risk_level,
    }

openness_keywords = [
    "open", "transparent", "accessible", "receptive", "welcoming", "approachable", 
    "honest", "candid", "forthcoming", "clear", "unconcealed", "unobstructed", 
    "unreserved", "unrestricted", "unhidden", "frank", "vulnerable", "genuine", 
    "transparent communication", "open-minded", "open-hearted", "open to suggestions", 
    "inviting", "inclusive", "sharing", "authentic", "unafraid", "unashamed", "unpretentious", 
    "out in the open", "straightforward", "forthright", "unvarnished", "unfiltered", 
    "unrestricted access", "freely given", "honest exchange", "direct", "non-judgmental", 
    "unreserved attitude", "reliable communication", "inviting conversation", "exploratory", 
    "unobstructed views", "approachable demeanor", "accepting", "understanding", "empathetic", 
    "vocal", "unbiased", "open to feedback", "ready to listen", "unfettered", "frankness", 
    "honesty", "willing to share", "eager to collaborate", "progressive", "genuine intent", 
    "free-flowing", "receptiveness", "open to ideas", "approachability", "inclusive environment", 
    "equal opportunity", "transparent practices", "open access", "no barriers", "expressive", 
    "accepting new ideas", "welcoming attitude", "freedom of expression", "non-restrictive", 
    "willingness to learn", "open to interpretation", "open to change", "open space", 
    "open conversation", "informative", "enlightening", "clear communication", "unreserved sharing", 
    "easy to talk to", "accessible information", "equal dialogue", "welcoming approach", "tolerant", 
    "free exchange", "flexible", "expansive", "liberal", "open exchange", "adaptive", "fluid", 
    "open-ended", "sharing knowledge", "unobstructed dialogue", "ready to engage", "open to all", 
    "open to different perspectives", "transparent exchange", "unified", "honesty in action", 
    "exploration", "forward-thinking", "unconstrained", "inclusive discourse", "unopposed", 
    "unencumbered", "openness to collaboration", "open communication", "mutual understanding", 
    "unopposed viewpoints", "unveiling", "no boundaries", "unconfined", "free exchange of ideas", 
    "unlocked", "transparent dialogue", "acceptance", "open exchange of thoughts", 
    "open-mindedness", "free-flowing conversation", "unveiling ideas", "sharing knowledge freely", 
    "exchanging freely", "non-limited", "non-conformist", "participatory", "transparent outlook", 
    "open systems", "no walls", "democratic", "creative freedom", "open world", "accessible platform", 
    "unfettered opportunity", "reliable access", "collaborative", "free expression", "embracing change", 
    "approachable space", "non-restrictive communication", "inclusive dialogue", "freedom to express", 
    "flexible thinking", "open culture", "adaptable", "open thinking", "open source", "free and open", 
    "willingness to collaborate", "unrestricted sharing", "open agenda", "conversational", "welcoming mindset", 
    "encouraging", "unrestricted thinking", "inviting change", "non-censored", "no restrictions", 
    "sharing openly", "communicating freely", "freedom of speech", "welcoming discourse", 
    "open viewpoints", "expanding horizons", "non-judgmental space", "unlimited thinking", 
    "embracing diversity", "welcoming of all", "unfiltered opinion", "free-flowing ideas", 
    "open space for all", "constructive communication", "open to hearing", "empathy", "non-restrictive path", 
    "collaboration", "spontaneous", "open worldviews", "opening doors", "welcoming diversity", 
    "inclusive sharing", "generosity of spirit", "outspoken", "unbarred", "expansive thinking", 
    "mindful exchange", "freedom to speak", "participation", "unopposed expression", "inviting new ideas", 
    "genuine sharing", "constructive criticism", "participatory space", "eager to help", "open to improvement", 
    "genuine conversation", "approaching new ideas", "sharing insights", "welcoming different viewpoints", 
    "inclusive mindset", "uninhibited", "open conversation space", "no judgment", "transparent process", 
    "open perspective", "clear-cut", "clarity", "intellectual freedom", "candid exchange", 
    "open to collaboration", "uncomplicated", "uninfluenced", "accepting of difference", "genuine feedback", 
    "acceptance of change", "unrestricted perspectives", "freedom of thought", "welcoming feedback", 
    "inclusive conversations", "generous listening", "boundless", "collaborative space", "honest sharing", 
    "accepting feedback", "free access", "unbound", "safe space", "constructive openness", 
    "open to suggestions", "unlimited perspectives", "open to all ideas", "listening ear", "uncensored", 
    "non-limited communication", "embracing diverse thoughts", "without restriction", "open culture", 
    "transparent process", "access to knowledge", "participative engagement", "inclusive environment", 
    "honest dialogue", "open discourse", "freedom of thought", "contemplative", "cooperative", 
    "honest exchange of ideas", "free thinking", "clear expression", "inviting atmosphere", 
    "open expression", "unlimited freedom", "inviting new perspectives", "encouraging collaboration"
]

def detect_openness(text, openness_keywords, similarity_threshold=80):    
    openness_count = 0

    for keyword in openness_keywords:
        best_match, score, _ = process.extractOne(keyword, text, scorer=fuzz.partial_ratio)
        if score >= similarity_threshold:
            openness_count += 1

    total_words = len(text.split())

    if openness_count == 0:
        return {
            "Message": "No signals of openness to improve detected",
            "Openness Keywords": 0,
            "Total Words": total_words,
            "Openness Level": "No Evident"
        }
    openness_ratio = openness_count / total_words

    if openness_ratio > 0.2:
        openness_level = "Highly open to improvement (frequent use of openness-related words)"
    elif openness_ratio > 0.1:
        openness_level = "Moderately open to improvement"
    else:
        openness_level = "Low openness to improvement detected (minimal use of openness-related words)"

    result = {
        "Openness Keywords": openness_count,
        "Total Words": total_words,
        "Openness Ratio": round(openness_ratio, 2),
        "Openness Level": openness_level,
    }
    return result

gender_keywords = [
    "he", "she", "him", "her", "his", "hers", "they", "them", "their", "theirs",
    "man", "woman", "boy", "girl", "gentleman", "lady", "lad", "lass",
    "male", "female", "non-binary", "transgender", "cisgender", "genderfluid",  
    "agender", "bigender", "genderqueer", "two-spirit", 
    "mr", "mrs", "ms", "miss", "mx", "madam", "sir",  
    "father", "mother", "son", "daughter", "brother", "sister",  
    "uncle", "aunt", "nephew", "niece", "husband", "wife", 
    "policeman", "policewoman", "fireman", "stewardess", "chairman", "chairwoman",  
    "expecting mother", "stay-at-home dad", "working mom", "career woman",  
    "manpower", "womanpower", "maternity", "paternity",
    "masculine", "feminine", "manly", "womanly", "effeminate", "tomboy",
    "gay", "lesbian", "bisexual", "queer", "heterosexual", "homosexual",  
    "partner", "same-sex", "opposite-sex",
    "housewife", "breadwinner", "girly",  
    "man up", "act like a lady", "real man", "bossy",
    "il", "elle", "él", "ella", "er", "sie"
]

race_keywords = [
    "Asian", "Black", "White", "Hispanic", "Latino", "Latina", "Latinx",  
    "Indian", "African", "Caucasian", "Middle Eastern", "Native American",  
    "Indigenous", "Pacific Islander", "Caribbean",  
    "South Asian", "East Asian", "Southeast Asian", "West African",  
    "North African", "African American", "Afro-Caribbean", "Afro-Latino",  
    "Arab", "Persian", "Jewish", "Kurdish", "Berber", "Turkic",  
    "Hmong", "Punjabi", "Bengali", "Tamil", "Pashtun",  
    "Chinese", "Japanese", "Korean", "Filipino", "Thai", "Vietnamese",  
    "Mexican", "Brazilian", "Argentinian", "Colombian", "Peruvian",  
    "Egyptian", "Moroccan", "Somali", "Ethiopian",  
    "French Algerian", "Indian American", "Bangladeshi",
    "Aboriginal", "First Nations", "Māori", "Inuit",  
    "Roma", "Gypsy","Creole", "Mulatto","Moors", "Zionist", "Ashkenazi", "Sephardic",  
    "colored", "negro", "Oriental", "Eskimo", "half-breed",  
    "tribal", "primitive", "exotic", "ethnic minority",  
    "BIPOC", "POC", "Mixed-race", "Biracial", "Multiracial",  
    "foreigner", "illegal alien", "third-world", "model minority",  
    "ghetto", "urban","blanco", "negro","mulato","ethnie", "tribu"
]

age_keywords = [
    "young", "old", "senior", "junior", "middle-aged", "elderly",  
    "youth", "teen", "teenager", "minor", "adolescent", "child",  
    "adult", "middle-aged", "retired", "aging", "geriatric",  
    "overage", "underage", "mature", "elder",  
    "experienced", "inexperienced", "fresh", "seasoned", "veteran",  
    "entry-level", "beginner", "novice", "mid-career", "early-career",  
    "late-career", "tenured", "intern", "apprentice", "trainee",  
    "rookie", "prodigy", "expert", "seniority",  
    "millennial", "Gen Z", "Gen X", "baby boomer", "boomer",  
    "post-retirement", "pre-retirement", "working age", "prime age",  
    "too young", "too old", "past your prime", "past their prime",  
    "next generation", "future leader", "rising star",  
    "energetic youth", "outdated", "old-fashioned", "stuck in their ways",  
    "not adaptable", "slowing down", "mentally sharp", "overqualified",  
    "underqualified", "obsolete", "young blood", "gray hair",  
    "age gap", "generation gap", "senile", "fossil",  
    "retiree", "retirement age", "mandatory retirement",  
    "age restriction", "age limit", "overqualified due to age",  
    "early retirement", "late retirement", "too young to lead",  
    "too old to innovate","spry", "frail", "full of energy", "slow learner", "fast learner",  
    "adaptable", "rigid mindset", "old school", "tech-savvy",  
    "new generation mindset", "youthful perspective",  
]

import csv
import yaml
import os

input_file = "belief_action_clean.csv"
output_file = "belief_action_scored.yaml"

# -----------------------
# HYPER-DETAILED TAGGING LOGIC
# -----------------------
def tag_belief(text):
    text = text.lower()
    # 1. Social Alienation / Outsider
    if any(w in text for w in ["everyone else", "watching", "pretending", "movie", "ghost", "script", "belong", "postcard", "language", "audience", "cast", "stage", "play", "re-recorded","running in the background","pretend", "outside","don't know what that even means", "foreign", "glass", "bubble", "disconnected","picturing"]):
        return "social_alienation"
    # 2. Emotional Burden / Chronic Pressure
    elif any(w in text for w in ["heavy", "pressure", "overwhelmed", "exhausting", "stewing", "gutted", "weight", "mountain", "bracing", "suffocate", "flattened","erased", "anchor", "crushing", "lead", "stifling","Feel good? I… I don’t know what that even means anymore"]):
        return "emotional_burden"
    # 3. Low Self-Efficacy / Learned Helplessness
    elif any(w in text for w in ["don't know", "can't", "failed", "failing", "fail", "messing up", "wrong answer", "test", "quiz", "trip", "stare", "puzzle", "deadline", "assignment", "homework", "stare", "floor is going to give out","bottom", "stuck", "sink", "drowning"]):
        return "low_self_efficacy"
    # 4. Impostor Syndrome / Worthlessness
    elif any(w in text for w in ["deserve", "merit", "luck", "impostor", "fraud", "thief", "expired", "expiration date","lottery", "pathetic", "stupid", "mess", "shame", "wrong", "fundamentally", "broken", "flawed","feels good for a second","blows up"]):
        return "impostor_syndrome"
    # 5. Anhedonia / Emptiness / Numbness
    elif any(w in text for w in ["nothing", "boring", "fake", "empty", "quiet", "expired", "nobody's home", "flat", "stale", "smell", "throw myself out","words", "hollow", "void", "gray", "mute", "unfeeling"]):
        return "anhedonia_emptiness"
    # 6. Performance Identity / Perfectionism
    elif any(w in text for w in ["competent", "capable", "useful", "organizing", "steady", "solid", "good at school", "role", "managing enough", "got-it-all-figured-out","fun","poison the well", "identity", "productive", "achieve"]):
        return "performance_identity"
    # 7. Relational Friction / Protection
    elif any(w in text for w in ["worry them", "disappointment", "letting him down", "managing her", "mother", "dad", "mama bear", "burden", "soundproof window","fail","fear","fear was already packed","frustrating", "angry", "resentment", "hostile"]):
        return "relational_anxiety"
    # 8. Temporal Despair
    elif any(w in text for w in ["future", "focus", "ago", "years", "looking forward", "move", "ticking", "clock","time","what to expect", "never", "always", "waiting", "someday"]):
        return "temporal_despair"
    # 9. Metacognitive Noise (Thinking about thinking)
    elif any(w in text for w in ["thoughts", "brain", "mind", "thinking", "noticed", "realized", "aware", "internal monologue", "noise", "static","I am not sure I even knew what that was","i think"]):
        return "metacognitive_noise"
    return "other"

def tag_action(text):
    text = text.lower()
    # 1. Masking / Social Camouflage
    if any(w in text for w in ["copy", "watching", "pretend", "acting", "mask", "cues", "stage", "show", "faking", "costume", "lines", "usual part", "everything's fine fm", "play my usual part","script", "hide","sure", "smile", "nodding", "agreeing","borrowing","keeping things"]):
        return "masking"
    # 2. Emotional Suppression / Cognitive Numbing
    elif any(w in text for w in ["drown", "ignore", "stop", "hide", "quietly", "stop my brain", "stifle", "motions", "legs moving", "no script", "tell my brain", "refuses to get the memo","background","not built for","everything feels quiet", "push down", "numb", "tune out"]):
        return "suppression"
    # 3. Avoidance / Social Withdrawal
    elif any(w in text for w in ["avoid", "leave", "not come", "push them away", "run", "missed", "withdrawing", "throw myself out", "don't show", "keep it light", "holding a piece back","almost","didn't","waiting","them","boring", "cancelled", "stayed"]):
        return "avoidance"
    # 4. Hyper-Compensation / Compulsive Fixing
    elif any(w in text for w in ["managing", "sanding down", "fix", "toolbox", "organizing", "checked", "map", "plans", "clipboard", "organizing the fun", "answer that","ready", "i don't want","handle on my own","solid again", "clean", "list", "re-did"]):
        return "hyper_compensation"
    # 5. Somatic Regulation / Grounding
    elif any(w in text for w in ["breathing", "glass of water", "walking", "jumping", "physically", "sleep", "hike", "physical state","exhausting", "shower", "bed", "eat", "pulse"]):
        return "somatic_regulation"
    # 6. Self-Sabotage / Destructive Release
    elif any(w in text for w in ["suffocate","feel stupid", "stupid", "shatter", "trip", "fall", "blow up", "threw", "jumping", "give out", "wrong answer","right answer", "broke", "quit", "ruined","failed","evidence","prove","problem"]):
        return "self_sabotage"
    # 7. Interpersonal Management
    elif any(w in text for w in ["managing her", "managing her anxiety", "sand down", "keep calm", "handle on my own", "soothe", "reassure", "calm them"]):
        return "interpersonal_management"
    # 8. Analytical Ruminating (Action as mental work)
    elif any(w in text for w in ["analyze", "wondering", "figuring", "searching", "trying to understand", "questioning", "replaying","mystery","learned"]):
        return "analytical_rumination"
    return "other"# -----------------------
# REFINED ALIGNMENT LOGIC
# -----------------------
def calculate_alignment(belief, action):
    b_tag = tag_belief(belief)
    a_tag = tag_action(action)
    
    score = 0.5 
    
    # Logic: Certain tag combinations are naturally consistent (defenses)
    consistency_pairs = [
        ("social_alienation", "masking"),
        ("emotional_burden", "avoidance"),
        ("low_self_efficacy", "suppression"),
        ("relational_anxiety", "hyper_compensation"),
        ("impostor_syndrome", "masking")
    ]
    
    if (b_tag, a_tag) in consistency_pairs:
        score += 0.3
        
    # Logic: Dissonance (Internal pain vs External "Fixing")
    if b_tag == "emotional_burden" and a_tag == "hyper_compensation":
        score -= 0.2 # The "Burnout" score
        
    if b_tag == "anhedonia_emptiness" and a_tag == "masking":
        score += 0.2 # Consistent: feeling nothing but acting like everything is fine
        
    score = round(max(0.1, min(1.0, score)), 2)
    
    if score >= 0.75: label = "High Consistency"
    elif score >= 0.45: label = "Moderate"
    else: label = "Dissonant"
    
    return score, label

# -----------------------
# MAIN PROCESSING (Remains same as your previous working version)
# -----------------------
data = {"patients": {}}

if not os.path.exists(input_file):
    print(f"❌ Error: {input_file} not found.")
else:
    with open(input_file, newline='', encoding="utf-8-sig") as f:
        lines = f.readlines()
        header_index = 0
        for i, line in enumerate(lines):
            if "BELIEF" in line.upper() and "ACTION" in line.upper():
                header_index = i
                break
        
        f.seek(0)
        for _ in range(header_index): next(f)
            
        sep = ";" if ";" in lines[header_index] else ","
        reader = csv.DictReader(f, delimiter=sep)
        reader.fieldnames = [n.strip().upper() for n in reader.fieldnames]

        for row in reader:
            p_name = row.get("PATIENT", "unknown").strip().lower()
            belief = row.get("BELIEF", "").strip()
            action = row.get("ACTION", "").strip()

            if not belief and not action: continue

            if p_name not in data["patients"]:
                data["patients"][p_name] = []

            score, label = calculate_alignment(belief, action)

            data["patients"][p_name].append({
                "id": len(data["patients"][p_name]) + 1,
                "belief": belief,
                "action": action,
                "tags": {
                    "belief_type": tag_belief(belief),
                    "action_type": tag_action(action)
                },
                "alignment": {
                    "score": score,
                    "label": label
                }
            })

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    
    print(f"✅ YAML generated! Detailed tags applied.")
    for p, pairs in data["patients"].items():
        others = sum(1 for x in pairs if x["tags"]["belief_type"] == "other")
        print(f"   - {p.capitalize()}: {len(pairs)} rows ({others} still marked as 'other')")
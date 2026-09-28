## Idea: Train a model to recognize IVR system like AF, FK or the Swedish Police

### Goals:
1. Train the model to recognize queue number - when the robot operator says "Din plats är : <number>

### Choose an architecture of one of the following:

(A)
1. Pythons library: ```librosa```, ```pydub``` to record the call
2. OpenAI:s Whisper to transcribe to text
3. Regexp to extract "din plats i kön är 47"

(B)
1. NLU-based 

(C)
1. Use ios library ```AVAudioRecorder```


## Process
Task 1: Fetch and prepare data
  ↓
Task 2: Train the model (this is where the neural network training happens)
  ↓
Task 3: Validate on test set
  ↓
Task 4: Deploy model to production



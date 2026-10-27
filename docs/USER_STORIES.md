# Audio Numbers Detection Lab — User Stories

## Story 1: Record Training Data

**As a** learner building an audio classifier  
**I want to** record audio clips of spoken numbers 1-5  
**So that** I have labeled data to train the model on

### Acceptance Criteria
- [ ] Record 10 clips per number (50 total)
- [ ] Vary tone, speed, and voice characteristics
- [ ] Save as WAV files in `data/{number}/` folders
- [ ] Split: 7 for training, 1 for validation, 2 for testing

---

## Story 2: Extract Audio Features

**As a** learner understanding audio processing  
**I want to** extract MFCC features from audio files using librosa  
**So that** the model has numerical data to learn from (not raw waveforms)

### Acceptance Criteria
- [ ] Load all audio files from data folders
- [ ] Extract MFCC coefficients for each clip
- [ ] Output feature matrix (N samples × M features)
- [ ] Handle edge cases (short clips, silence)

---

## Story 3: Train the Classifier

**As a** learner validating my understanding of ML  
**I want to** train a RandomForest classifier on the extracted features  
**So that** the model learns to predict numbers from audio

### Acceptance Criteria
- [ ] Split data into train/validation/test (70/15/15)
- [ ] Fit RandomForest on training set
- [ ] Monitor validation accuracy during development
- [ ] Save trained model to disk

---

## Story 4: Evaluate Performance

**As a** learner checking if the model works  
**I want to** test the model on unseen data  
**So that** I know if it actually learned or just memorized

### Acceptance Criteria
- [ ] Report accuracy on test set
- [ ] Show classification report (precision, recall per number)
- [ ] Compare train vs validation vs test accuracy
- [ ] Identify overfitting if present

let mediaRecorder;
let audioChunks = [];
let waveSurfer;
const nextBtn = document.getElementById("nextBtn");
const startRecordingBtn = document.getElementById("startRecording");
const stopRecordingBtn = document.getElementById("stopRecording");
const playAudioBtn = document.getElementById("playAudio");
const statusMessage = document.getElementById("status");

// Initialize WaveSurfer
waveSurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'violet',
    progressColor: 'purple',
    cursorColor: '#ffa500',
    barWidth: 2,
    height: 100,
    responsive: true
});
nextBtn.addEventListener("click", async () => {
    const response = await fetch('/next', { method: 'POST' });
    const data = await response.json();
    document.getElementById("currentWord").textContent = data.word;
    referenceText.textContent = "";
    transcriptionText.textContent = "";
    totalScore.textContent = "";
    phonemeScores.innerHTML = "";
});
startRecordingBtn.addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    audioChunks = [];
    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioURL = URL.createObjectURL(audioBlob);

        // Load the recorded audio into WaveSurfer
        waveSurfer.load(audioURL);

        playAudioBtn.disabled = false;

        // Handle form submission to the backend
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();

        // Update UI with results
        document.getElementById("referenceText").textContent = data.reference;
        document.getElementById("transcriptionText").textContent = data.transcription;
        document.getElementById("totalScore").textContent = `${data.alignment_score.toFixed(2)}%`;
        phonemeScores.innerHTML = data.scores.map(score => {
            const color = score.score >= 70 ? "green" : score.score >= 52 ? "orange" : "red";
            return `<span style="color:${color};">${score.phoneme}: ${score.score.toFixed(2)}%</span>`;
        }).join('');
    };

    mediaRecorder.start();
    statusMessage.textContent = "Enregistrement en cours...";
    startRecordingBtn.disabled = true;
    stopRecordingBtn.disabled = false;
});

stopRecordingBtn.addEventListener("click", () => {
    mediaRecorder.stop();
    statusMessage.textContent = "Enregistrement arrété.";
    startRecordingBtn.disabled = false;
    stopRecordingBtn.disabled = true;
});

playAudioBtn.addEventListener("click", () => {
    waveSurfer.playPause();
});

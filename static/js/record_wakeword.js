var gumStream; // Stream from getUserMedia()
var rec; // Recorder.js object
var input; // MediaStreamAudioSourceNode we'll be recording
var recordingNotStopped; // User pressed record button and keep talking, still not stop button pressed
const trackLengthInMS = 10000; // Length of audio chunk in miliseconds
const maxMS = 10000; // Number of mili seconds we support per recording (1 second)


//Extend the Recorder Class and add clear() method
// Recorder.prototype.step = function () {
    // this.clear();
// };
const form = document.getElementById('wakeword');

var wakewordName = "dummy"

form.addEventListener('submit', (event) => {
    // handle the form data
    event.preventDefault();
    // console.log(form);
    wakewordName = form.elements['name'].value;
    console.log(wakewordName);
});



// Shim for AudioContext when it's not available.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");

//Event handlers for above 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

//Asynchronous function to stop the recoding in each second and export blob to a wav file
const sleep = time => new Promise(resolve => setTimeout(resolve, time));



const asyncFn = async() => {
  var elapsedMS = 0;
  for (let i = 0; i < maxMS; i++) {

    if (recordingNotStopped) {
      elapsedMS += trackLengthInMS;
      rec.record();
      await sleep(trackLengthInMS);
      rec.stop();
      if (elapsedMS >= maxMS) {
        console.log("max length");
        stopRecording();
      }

      //stop microphone access
      // gumStream.getAudioTracks()[0].stop();

      //Create the wav blob and pass it on to createWaveBlob
      rec.exportWAV(createWaveBlob);
      rec.clear();
    }
  }
}

function startRecording() {
  console.log("recordButton clicked");
  recordingNotStopped = true;
  var constraints = {
    audio: true,
    video: false
  }

  recordButton.disabled = true;
  stopButton.disabled = false;

  //Using the standard promise based getUserMedia()
  navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {

    //Create an audio context after getUserMedia is called
    audioContext = new AudioContext();

    // Assign to gumStream for later use
    gumStream = stream;

    //Use the stream
    input = audioContext.createMediaStreamSource(stream);

    //Create the Recorder object and configure to record mono sound (1 channel)
    rec = new Recorder(input, {
      numChannels: 1
    });

    //Call the asynchronous function to split and export audio
    // filename = getFileName()

    asyncFn();
    console.log("Recording started");

  }).catch(function(err) {
    //Enable the record button if getUserMedia() fails
    recordButton.disabled = false;
    stopButton.disabled = true;
  });
}

function stopRecording() {
  console.log("stopButton clicked");
  recordingNotStopped = false;

  //disable the stop button and enable the record button to  allow for new recordings
  stopButton.disabled = true;
  recordButton.disabled = false;

  //Set the recorder to stop the recording
  rec.stop();

  //stop microphone access
  gumStream.getAudioTracks()[0].stop();
}

function createWaveBlob(blob) {


  // var url = URL.createObjectURL(blob);

  //Convert the blob to a wav file and call the sendBlob function to send the wav file to the server
  // var convertedfile = new File([blob], 'filename.wav');
  fetch(`/accept_wakeword/`+ wakewordName, {method:"POST", body:blob})
                .then(response => console.log(response.text()))
    ;
  // sendBlob(convertedfile);
}

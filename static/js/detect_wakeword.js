var gumStream; // Stream from getUserMedia()
var rec; // Recorder.js object
var input; // MediaStreamAudioSourceNode we'll be recording
var recordingNotStopped; // User pressed record button and keep talking, still not stop button pressed
const trackLengthInMS = 500; // Length of audio chunk in miliseconds
const maxNumOfSecs = 1000; // Number of mili seconds we support per recording (1 second)


var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");

var ts = Math.round((new Date()).getTime() / 1000);


var availableWakewords = getWakewords()

var wakewordName = "dummy"


document.getElementById("form").addEventListener('submit', (event) => {

    event.preventDefault();
    var select = document.getElementById('wakewords');
    var value = select.options[select.selectedIndex].value;
    wakewordName = value;

    console.log(wakewordName);
});

//Event handlers for above 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

//Asynchronous function to stop the recoding in each second and export blob to a wav file
const sleep = time => new Promise(resolve => setTimeout(resolve, time));

const asyncFn = async() => {
  for (let i = 0; i < maxNumOfSecs; i++) {
    if (recordingNotStopped) {
      rec.record();
      await sleep(trackLengthInMS);
      rec.stop();

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

//Handles consumption of audio through Flask endpoint
async function createWaveBlob(blob) {

  let wakeCheck = await fetch(`/audio_reciever/${wakewordName}/${ts}`, {method:"POST", body:blob})
                 .then((response) =>  {
      return response.json();
    })
  if (wakeCheck.result != 'none_detected'){
  document.querySelector("#response").innerHTML = '<h1>' + wakeCheck.result +'</h1>';

} else {
  document.querySelector("#response").innerHTML = '<h1></h1>';
}
return wakeCheck.result

}

//Loads available wakewords for dropdown (via Flask endpoint)
async function getWakewords() {

  let wakewords = await fetch(`/get_available_wakewords`)
                 .then((response) =>  {
      return response.json();
    })
    .then(data => {
      const html = data.wakewords.map(wakeword => {
        return `<option value="${wakeword}">${wakeword}</option>`
      })
      document.querySelector("#wakewords").innerHTML = html;
    })

}

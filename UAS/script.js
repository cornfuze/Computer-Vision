// Impor MediaPipe
import { HandLandmarker, FilesetResolver, DrawingUtils } from './mediapipe_local/vision_bundle.mjs';

// Elemen HTML
const video = document.getElementById('webcam');
const canvasElement = document.getElementById('outputCanvas');
const canvasCtx = canvasElement.getContext('2d');
const webcamButton = document.getElementById('webcamButton');

// Cesium Setup
Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlN2IwN2ZiZS1jMTVlLTRkZmUtOGM4YS0zMjRmMWM4MWQzMTIiLCJpZCI6MzA4Mjk5LCJpYXQiOjE3NDg4MjE1MTl9.Pes91ljWIxyD0usE062T0tpQyuw4Z6R59wl8uNSJLeo';
let viewer;

function initializeCesium() {
    if (typeof Cesium !== 'undefined') {
        viewer = new Cesium.Viewer('cesiumContainer', {
            animation: false,
            fullscreenButton: false,
            geocoder: false,
            homeButton: false,
            infoBox: true,
            sceneModePicker: false,
            selectionIndicator: true,
            timeline: false,
            navigationHelpButton: false,
            
            sceneMode: Cesium.SceneMode.SCENE3D,
            contextOptions: { webgl: { alpha: true } },
            skyAtmosphere: false, 
            skyBox: false,

            imageryProvider: new Cesium.OpenStreetMapImageryProvider({
                url: 'https://a.tile.openstreetmap.org/'
            }),
            
        });

        if (viewer.scene) {
            viewer.scene.backgroundColor = Cesium.Color.TRANSPARENT;
            if (viewer.scene.globe) {
                viewer.scene.globe.enableLighting = true;
            }
            viewer.scene.screenSpaceCameraController.minimumZoomDistance = 100000; // 100 km
            viewer.scene.screenSpaceCameraController.enableTilt = false;
        }
        
        console.log("Cesium Viewer siap.");
    } else {
        console.error("Pustaka Cesium tidak ditemukan.");
    }
}
initializeCesium();

// MediaPipe Hand Landmarker Setup
let handLandmarker = undefined;
let runningMode = "VIDEO";
let webcamRunning = false;
let lastVideoTime = -1;
let handLandmarksData = [];
let handHandednessData = [];
let drawingUtils;

const visionTaskOptions = {
    baseOptions: {
        modelAssetPath: `./mediapipe_local/hand_landmarker.task`,
        delegate: "GPU"
    },
    runningMode: runningMode,
    numHands: 2
};

async function createHandLandmarker() {
    if (!FilesetResolver || !HandLandmarker || !DrawingUtils) {
        console.error("Gagal mengimpor FilesetResolver, HandLandmarker, atau DrawingUtils.");
        webcamButton.innerText = "Error: MediaPipe Gagal Dimuat";
        return;
    }
    const filesetResolver = await FilesetResolver.forVisionTasks("./mediapipe_local/wasm");
    try {
        handLandmarker = await HandLandmarker.createFromOptions(filesetResolver, visionTaskOptions);
        webcamButton.disabled = false;
        webcamButton.innerText = "Aktifkan Webcam";
        console.log("HandLandmarker siap.");
        if (canvasCtx) drawingUtils = new DrawingUtils(canvasCtx);
    } catch (error) {
        console.error("Gagal membuat HandLandmarker:", error);
        webcamButton.innerText = "Error: Model Tangan Gagal Dimuat";
    }
}
createHandLandmarker();

webcamButton.addEventListener('click', enableCam);

function enableCam(event) {
    if (!handLandmarker) {
        console.log("Tunggu! HandLandmarker belum siap atau gagal dimuat.");
        return;
    }
    webcamRunning = !webcamRunning;
    if (webcamRunning) {
        webcamButton.innerText = "Nonaktifkan Webcam";
        
        const constraints = {
            video: {
                width: { ideal: 1920 },
                height: { ideal: 1080 },
            }
        };

        navigator.mediaDevices.getUserMedia(constraints)
            .then((stream) => {
                video.srcObject = stream;
                video.addEventListener('loadeddata', () => {
                    console.log("Webcam stream active.");
                    console.log("Actual video resolution: " + video.videoWidth + "x" + video.videoHeight);
                    canvasElement.width = video.videoWidth;
                    canvasElement.height = video.videoHeight;
                    predictWebcam();
                });
            })
            .catch((err) => {
                console.error("Error mengakses webcam dengan constraints spesifik: ", err.name, err.message);
                console.log("Mencoba lagi dengan constraints default...");
                const defaultConstraints = { video: true };
                navigator.mediaDevices.getUserMedia(defaultConstraints)
                    .then((stream) => {
                        video.srcObject = stream;
                        video.addEventListener('loadeddata', () => {
                            console.log("Webcam stream active (default constraints).");
                            console.log("Actual video resolution (default): " + video.videoWidth + "x" + video.videoHeight);
                            canvasElement.width = video.videoWidth;
                            canvasElement.height = video.videoHeight;
                            predictWebcam();
                        });
                    })
                    .catch((defaultErr) => {
                        console.error("Error mengakses webcam dengan default constraints: ", defaultErr.name, defaultErr.message);
                        webcamRunning = false;
                        webcamButton.innerText = "Aktifkan Webcam";
                    });
            });
    } else {
        webcamButton.innerText = "Aktifkan Webcam";
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        if(canvasCtx) canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        handLandmarksData = [];
        handHandednessData = [];
    }
}

async function predictWebcam() {
    if (!webcamRunning || !handLandmarker || !video.srcObject || video.paused || video.ended) {
        if (webcamRunning && video.srcObject && (video.paused || video.ended)) webcamRunning = false;
        return;
    }
    if (canvasElement.width !== video.videoWidth || canvasElement.height !== video.videoHeight) {
        canvasElement.width = video.videoWidth;
        canvasElement.height = video.videoHeight;
    }
    let startTimeMs = performance.now();
    if (video.currentTime !== lastVideoTime) {
        lastVideoTime = video.currentTime;
        try {
            const results = handLandmarker.detectForVideo(video, startTimeMs);
            handLandmarksData = results.landmarks;
            handHandednessData = results.handedness;
        } catch (error) {
            console.error("Error saat deteksi tangan:", error);
            handLandmarksData = []; handHandednessData = [];
        }
    }

    if(canvasCtx) canvasCtx.save();
    if(canvasCtx) canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    if (drawingUtils && handLandmarksData && handLandmarksData.length > 0) {
        for (let i = 0; i < handLandmarksData.length; i++) {
            const landmarks = handLandmarksData[i];
            const handednessInfo = handHandednessData[i] && handHandednessData[i][0];
            const handedness = handednessInfo ? handednessInfo.categoryName : "Unknown";

            let connectorColor = 'rgba(0, 255, 0, 0.7)'; 
            let landmarkBaseFillColor = 'rgba(0, 200, 0, 0.7)'; 

            if (handedness === 'Right') { 
                connectorColor = 'rgba(0, 0, 255, 0.7)'; 
                landmarkBaseFillColor = 'rgba(0, 0, 200, 0.7)'; 
            }

            drawingUtils.drawConnectors(
                landmarks, HandLandmarker.HAND_CONNECTIONS,
                { color: connectorColor, lineWidth: 3 }
            );
            drawingUtils.drawLandmarks(
                landmarks, 
                { fillColor: landmarkBaseFillColor, color: connectorColor, radius: 3 }
            );

            const thumbTip = landmarks[4];
            const indexTip = landmarks[8];
            const pinchPointsToDraw = [thumbTip, indexTip];
            
            if (canvasCtx) {
                canvasCtx.fillStyle = "rgba(255, 0, 0, 0.9)"; 
                const pinchLandmarkRadius = 6;
                for (const point of pinchPointsToDraw) {
                    if (point) {
                        const canvasX = point.x * canvasElement.width;
                        const canvasY = point.y * canvasElement.height;
                        canvasCtx.beginPath();
                        canvasCtx.arc(canvasX, canvasY, pinchLandmarkRadius, 0, 2 * Math.PI);
                        canvasCtx.fill();
                    }
                }
            }
        }
        if (viewer) controlCesiumWithHand(handLandmarksData, handHandednessData);
    }
    if(canvasCtx) canvasCtx.restore();
    if (webcamRunning) window.requestAnimationFrame(predictWebcam);
}

// --- LOGIKA KONTROL ---
let rightHandState = {
    isPinching: false,
    initialPinchDistance: 0,
};
let leftHandState = {
    isPinching: false,
    initialPinchScreenPos: null,
    lastPinchScreenPos: null
};

const PINCH_THRESHOLD_START = 0.07; 
const PINCH_THRESHOLD_END = 0.20; 

function calculateNormalizedDistance(p1, p2) {
    if (!p1 || !p2) return Infinity;
    const dx = p1.x - p2.x; const dy = p1.y - p2.y;
    return Math.sqrt(dx * dx + dy * dy);
}
function getMidpoint(p1, p2) {
    if (!p1 || !p2) return { x: 0, y: 0};
    return { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };
}

function processRightHand(landmarks) { 
    const thumbTip = (landmarks && landmarks.length > 4 && landmarks[4] !== undefined) ? landmarks[4] : null;
    const indexTip = (landmarks && landmarks.length > 8 && landmarks[8] !== undefined) ? landmarks[8] : null;

    if (!thumbTip || !indexTip) {
        if (rightHandState.isPinching) {
            rightHandState.isPinching = false;
        }
        return;
    }
    const currentPinchDistance = calculateNormalizedDistance(thumbTip, indexTip);

    if (!rightHandState.isPinching && currentPinchDistance < PINCH_THRESHOLD_START) {
        rightHandState.isPinching = true;
        rightHandState.initialPinchDistance = currentPinchDistance;
    } else if (rightHandState.isPinching && currentPinchDistance > PINCH_THRESHOLD_END) {
        rightHandState.isPinching = false;
    }

    if (rightHandState.isPinching && viewer && viewer.camera && viewer.camera.positionCartographic && viewer.scene && viewer.scene.globe && viewer.scene.globe.ellipsoid) {
        const deviation = currentPinchDistance - rightHandState.initialPinchDistance;
        const zoomSensitivity = 0.2; // Sesuaikan ini untuk kecepatan zoom
        const currentCameraHeight = viewer.camera.positionCartographic.height;
        const deadZone = 0.002;

        if (Math.abs(deviation) > deadZone) {
            let moveAmount = -deviation * currentCameraHeight * zoomSensitivity;
            const maxMovePerFrame = currentCameraHeight * 0.06; 
            moveAmount = Math.max(-maxMovePerFrame, Math.min(maxMovePerFrame, moveAmount));

            if (deviation < 0) { 
                const minHeightAboveSurface = 1500000; 
                if (currentCameraHeight - Math.abs(moveAmount) > minHeightAboveSurface) {
                    viewer.camera.moveForward(Math.abs(moveAmount));
                } else {
                    const allowedMoveAmount = currentCameraHeight - minHeightAboveSurface;
                    if (allowedMoveAmount > 0) {
                        viewer.camera.moveForward(allowedMoveAmount);
                    }
                }
            } else { 
                viewer.camera.moveBackward(Math.abs(moveAmount));
            }
        }
    }
}

function processLeftHand(landmarks) { 
    const thumbTip = (landmarks && landmarks.length > 4 && landmarks[4] !== undefined) ? landmarks[4] : null;
    const indexTip = (landmarks && landmarks.length > 8 && landmarks[8] !== undefined) ? landmarks[8] : null;
    const pinchMidPoint = (thumbTip && indexTip) ? getMidpoint(thumbTip, indexTip) : null;
    const currentPinchDistance = (thumbTip && indexTip) ? calculateNormalizedDistance(thumbTip, indexTip) : Infinity;

    if (!thumbTip || !indexTip || !pinchMidPoint) return;

    if (!leftHandState.isPinching && currentPinchDistance < PINCH_THRESHOLD_START) {
        leftHandState.isPinching = true;
        leftHandState.initialPinchScreenPos = { x: pinchMidPoint.x, y: pinchMidPoint.y };
        leftHandState.lastPinchScreenPos = { x: pinchMidPoint.x, y: pinchMidPoint.y };
    } else if (leftHandState.isPinching && currentPinchDistance > PINCH_THRESHOLD_END) {
        leftHandState.isPinching = false;
    }

    if (leftHandState.isPinching && viewer && viewer.camera) {
        const deltaX = pinchMidPoint.x - leftHandState.lastPinchScreenPos.x;
        const deltaY = pinchMidPoint.y - leftHandState.lastPinchScreenPos.y;
        const panSpeedFactor = 0.05;
        const panMultiplier = 45; 

        if (Math.abs(deltaX) > 0.001) {
            if (deltaX > 0) viewer.camera.rotateRight(panSpeedFactor * Math.abs(deltaX * panMultiplier));
            else viewer.camera.rotateLeft(panSpeedFactor * Math.abs(deltaX * panMultiplier));
        }
        if (Math.abs(deltaY) > 0.001) {
            if (deltaY > 0) viewer.camera.rotateDown(panSpeedFactor * Math.abs(deltaY * panMultiplier));
            else viewer.camera.rotateUp(panSpeedFactor * Math.abs(deltaY * panMultiplier));
        }
        leftHandState.lastPinchScreenPos = { x: pinchMidPoint.x, y: pinchMidPoint.y };
    }
}

function controlCesiumWithHand(allHandLandmarks, allHandHandedness) {
    if (!viewer || !allHandLandmarks || allHandLandmarks.length === 0 || !allHandHandedness || allHandHandedness.length !== allHandLandmarks.length) {
        if (rightHandState.isPinching && (!allHandLandmarks || allHandLandmarks.findIndex((_,idx) => allHandHandedness[idx] && allHandHandedness[idx][0] && allHandHandedness[idx][0].categoryName === 'Right') === -1)) {
            rightHandState.isPinching = false;
        }
        if (leftHandState.isPinching && (!allHandLandmarks || allHandLandmarks.findIndex((_,idx) => allHandHandedness[idx] && allHandHandedness[idx][0] && allHandHandedness[idx][0].categoryName === 'Left') === -1)) {
            leftHandState.isPinching = false;
        }
        return;
    }

    let rightHandDetectedThisFrame = false;
    let leftHandDetectedThisFrame = false;

    for (let i = 0; i < allHandLandmarks.length; i++) {
        const landmarks = allHandLandmarks[i];
        const handednessInfo = allHandHandedness[i] && allHandHandedness[i][0];
        if (!handednessInfo) continue;
        const handedness = handednessInfo.categoryName;

        if (handedness === 'Right') {
            rightHandDetectedThisFrame = true;
            processRightHand(landmarks);
        } else if (handedness === 'Left') {
            leftHandDetectedThisFrame = true;
            processLeftHand(landmarks);
        }
    }

    if (rightHandState.isPinching && !rightHandDetectedThisFrame) {
        rightHandState.isPinching = false;
    }
    if (leftHandState.isPinching && !leftHandDetectedThisFrame) {
        leftHandState.isPinching = false;
    }
}
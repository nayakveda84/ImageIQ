
const imageInput = document.getElementById("imageInput");
const originalImage = document.getElementById("originalImage");
const previewMessage = document.getElementById("previewMessage");

// Parameter controls
const foregroundThreshold =
    document.getElementById("foregroundThreshold");

const distanceThreshold =
    document.getElementById("distanceThreshold");

const backgroundSize =
    document.getElementById("backgroundSize");

// Update parameter displays
foregroundThreshold.addEventListener("input", function () {
    document.getElementById("foregroundDisplay").textContent =
        Number(this.value).toFixed(2);
});

distanceThreshold.addEventListener("input", function () {
    document.getElementById("distanceDisplay").textContent =
        Number(this.value).toFixed(2);
});

// Display selected image
function displayWatershedImage(file, imagePath = null) {
    const imageURL = imagePath || URL.createObjectURL(file);

    originalImage.src = imageURL;
    originalImage.style.display = "block";
    previewMessage.style.display = "none";
}

// Upload image
imageInput.addEventListener("change", function () {
    const file = this.files[0];

    if (!file) return;

    displayWatershedImage(file);
});

// Select sample image
async function selectWatershedSample(imagePath) {
    try {
        const response = await fetch(imagePath);

        if (!response.ok) {
            throw new Error("Could not load sample image. Check its path.");
        }

        const blob = await response.blob();

        const file = new File(
            [blob],
            imagePath.split("/").pop(),
            { type: blob.type || "image/jpeg" }
        );

        const transfer = new DataTransfer();
        transfer.items.add(file);
        imageInput.files = transfer.files;

        displayWatershedImage(file, imagePath);

    } catch (error) {
        alert(error.message);
    }
}

// Display backend result images
function showWatershedResult(imageId, messageId, base64Image) {
    const image = document.getElementById(imageId);
    const message = document.getElementById(messageId);

    image.src = "data:image/png;base64," + base64Image;
    image.style.display = "block";
    message.style.display = "none";
}

// Run watershed segmentation
async function processWatershed() {
    const file = imageInput.files[0];

    if (!file) {
        alert("Please upload or select a fruit image first.");
        return;
    }

    const formData = new FormData();

    formData.append("image", file);
    formData.append("foreground_threshold", foregroundThreshold.value);
    formData.append("background_size", backgroundSize.value);
    formData.append("distance_threshold", distanceThreshold.value);

    const button = document.querySelector(
        ".processing-section > button"
    );

    const originalText = button.textContent;

    button.disabled = true;
    button.textContent = "Segmenting fruits...";

    try {
        const response = await fetch(
            "http://127.0.0.1:5000/process-watershed",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Segmentation failed.");
        }

        showWatershedResult(
            "originalResult", "originalResultMessage",
            data.original_image
        );

        showWatershedResult(
            "preprocessedImage", "preprocessedMessage",
            data.preprocessed_image
        );

        showWatershedResult(
            "distanceImage", "distanceMessage",
            data.distance_image
        );

        showWatershedResult(
            "markerImage", "markerMessage",
            data.marker_image
        );

        showWatershedResult(
            "segmentedImage", "segmentedMessage",
            data.segmented_image
        );

        document.getElementById("fruitCount").textContent =
            data.fruit_count;

        document.getElementById("foregroundPixels").textContent =
            data.foreground_pixels;

        document.getElementById("regionCount").textContent =
            data.region_count;

        document.getElementById("analysisText").textContent =
            data.analysis;

    } catch (error) {
        alert("Error: " + error.message);
    } finally {
        button.disabled = false;
        button.textContent = originalText;
    }
}

// Reset experiment
function resetWatershed() {
    imageInput.value = "";

    originalImage.src = "";
    originalImage.style.display = "none";
    previewMessage.style.display = "block";

    const results = [
        ["originalResult", "originalResultMessage"],
        ["preprocessedImage", "preprocessedMessage"],
        ["distanceImage", "distanceMessage"],
        ["markerImage", "markerMessage"],
        ["segmentedImage", "segmentedMessage"]
    ];

    results.forEach(([imageId, messageId]) => {
        const image = document.getElementById(imageId);
        image.src = "";
        image.style.display = "none";

        document.getElementById(messageId).style.display = "block";
    });

    document.getElementById("fruitCount").textContent = "-";
    document.getElementById("foregroundPixels").textContent = "-";
    document.getElementById("regionCount").textContent = "-";

    document.getElementById("analysisText").textContent =
        "Upload an image and run watershed segmentation to view the analysis.";
}

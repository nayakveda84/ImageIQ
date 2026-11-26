
const imageInput = document.getElementById("imageInput");
const originalImage = document.getElementById("originalImage");
const previewMessage = document.getElementById("previewMessage");

const thresholdSlider = document.getElementById("thresholdValue");
const thresholdDisplay = document.getElementById("thresholdDisplay");

// Show selected image
imageInput.addEventListener("change", function () {
    const file = this.files[0];

    if (!file) return;

    originalImage.src = URL.createObjectURL(file);
    originalImage.style.display = "block";
    previewMessage.style.display = "none";
});

// Update threshold value
thresholdSlider.addEventListener("input", function () {
    thresholdDisplay.textContent = this.value;
});

// Convert image data to displayable URL
function showResult(imageId, base64Image, messageId) {
    const image = document.getElementById(imageId);
    const message = document.getElementById(messageId);

    image.src = "data:image/png;base64," + base64Image;
    image.style.display = "block";
    message.style.display = "none";
}

// Process White Top-Hat
async function processTopHat() {
    const file = imageInput.files[0];

    if (!file) {
        alert("Please upload a grayscale image first.");
        return;
    }

    const formData = new FormData();

    formData.append("image", file);
    formData.append("kernel_size", document.getElementById("kernelSize").value);
    formData.append("kernel_shape", document.getElementById("kernelShape").value);
    formData.append("threshold", thresholdSlider.value);

    const button = document.querySelector(".processing-section > button");
    const originalText = button.textContent;

    button.disabled = true;
    button.textContent = "Processing...";

    try {
        const response = await fetch("http://127.0.0.1:5000/process-tophat", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Image processing failed.");
        }

        showResult("openedImage", data.opened_image, "openedMessage");
        showResult("topHatImage", data.tophat_image, "topHatMessage");
        showResult("binaryImage", data.binary_image, "binaryMessage");

        document.getElementById("objectCount").textContent = data.object_count;
        document.getElementById("foregroundPixels").textContent = data.foreground_pixels;
        document.getElementById("connectivity").textContent = data.connectivity;

        document.getElementById("analysisText").textContent = data.analysis;

    } catch (error) {
        alert("Error: " + error.message);
    } finally {
        button.disabled = false;
        button.textContent = originalText;
    }
}

// Reset experiment
function resetTopHat() {
    imageInput.value = "";

    originalImage.src = "";
    originalImage.style.display = "none";
    previewMessage.style.display = "block";

    ["openedImage", "topHatImage", "binaryImage"].forEach(id => {
        const image = document.getElementById(id);
        image.src = "";
        image.style.display = "none";
    });

    ["openedMessage", "topHatMessage", "binaryMessage"].forEach(id => {
        document.getElementById(id).style.display = "block";
    });

    document.getElementById("objectCount").textContent = "-";
    document.getElementById("foregroundPixels").textContent = "-";
    document.getElementById("connectivity").textContent = "-";
    document.getElementById("analysisText").textContent =
        "Upload an image and run the experiment to view the analysis.";
}

async function selectTopHatSample(imagePath) {
    try {
        const response = await fetch(imagePath);

        if (!response.ok) {
            throw new Error("Could not load sample image.");
        }

        const blob = await response.blob();

        const file = new File(
            [blob],
            imagePath.split("/").pop(),
            { type: "image/jpeg" }
        );

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        imageInput.files = dataTransfer.files;

        originalImage.src = imagePath;
        originalImage.style.display = "block";
        previewMessage.style.display = "none";

    } catch (error) {
        alert(error.message);
    }
}

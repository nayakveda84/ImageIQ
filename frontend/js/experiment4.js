
const API_URL = "http://127.0.0.1:5000";

const digitInput = document.getElementById("digitInput");

let selectedDigitFile = null;
let previewURL = null;

// Display selected image
function showPreview(file) {
    if (previewURL) {
        URL.revokeObjectURL(previewURL);
    }

    previewURL = URL.createObjectURL(file);

    const preview = document.getElementById("digitOriginal");
    preview.src = previewURL;
    preview.style.display = "block";

    document.getElementById("digitPlaceholder").style.display = "none";
}

// Upload image from computer
digitInput.addEventListener("change", function () {
    const file = this.files[0];

    if (!file) return;

    selectedDigitFile = file;
    showPreview(file);
});

// Select sample image
async function selectDigitSample(imagePath) {
    try {
        const response = await fetch(imagePath);

        if (!response.ok) {
            throw new Error("Unable to load sample image: " + imagePath);
        }

        const blob = await response.blob();

        selectedDigitFile = new File(
            [blob],
            "sample_digit.png",
            { type: blob.type }
        );

        digitInput.value = "";

        showPreview(selectedDigitFile);

    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

// Process handwritten digit
async function processDigit() {
    if (!selectedDigitFile) {
        alert("Please upload or select a digit first.");
        return;
    }

    const formData = new FormData();
    formData.append("image", selectedDigitFile);

    document.getElementById("recognitionText").textContent =
        "Processing image...";

    try {
        const response = await fetch(`${API_URL}/process-digit`, {
            method: "POST",
            body: formData
        });

        const result = await response.json();
        
        console.log("FULL BACKEND RESPONSE:", result);


function displayResultImage(id, imageData) {
    const img = document.getElementById(id);

    img.onload = function () {
        console.log(
            id + " loaded:",
            img.naturalWidth,
            "x",
            img.naturalHeight
        );
    };

    img.onerror = function () {
        console.error(id + " failed to load.");
    };

    img.src = "data:image/png;base64," + imageData;

    img.style.display = "block";
    img.style.width = "100%";
    img.style.maxWidth = "320px";
    img.style.height = "auto";
    img.style.minHeight = "160px";
    img.style.objectFit = "contain";
}

displayResultImage("digitPreprocessed", result.preprocessed_image);
displayResultImage("digitBoundary", result.boundary_image);
displayResultImage("digitRegions", result.regional_image);


        document.getElementById("digitPreprocessed").src =
            "data:image/png;base64," + result.preprocessed_image;

        document.getElementById("digitBoundary").src =
            "data:image/png;base64," + result.boundary_image;

        document.getElementById("digitRegions").src =
            "data:image/png;base64," + result.regional_image;

        document.getElementById("predictedDigit").textContent =
            result.predicted_digit;

        document.getElementById("recognitionText").textContent =
            result.analysis;

        document.getElementById("descriptorResults").innerHTML =
            result.descriptor_comparison;

        document.getElementById("evaluationResults").innerHTML =
            result.evaluation;

    } catch (error) {
        console.error(error);

        document.getElementById("recognitionText").textContent =
            error.message;
    }
}

// Reset page
function resetDigit() {
    selectedDigitFile = null;
    digitInput.value = "";

    if (previewURL) {
        URL.revokeObjectURL(previewURL);
        previewURL = null;
    }

    [
        "digitOriginal",
        "digitPreprocessed",
        "digitBoundary",
        "digitRegions"
    ].forEach(id => {
        const img = document.getElementById(id);
        img.removeAttribute("src");

        if (id === "digitOriginal") {
            img.style.display = "none";
        }
    });

    document.getElementById("digitPlaceholder").style.display = "block";

    document.getElementById("predictedDigit").textContent = "--";

    document.getElementById("recognitionText").textContent =
        "Waiting for image processing...";

    document.getElementById("descriptorResults").innerHTML = "";
    document.getElementById("evaluationResults").innerHTML = "";
}

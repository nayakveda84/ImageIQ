
 let selectedImage = null;
 let originalChart = null;
let processedChart = null;


const imageInput = document.getElementById("imageInput");
const originalImage = document.getElementById("originalImage");
const previewMessage = document.getElementById("previewMessage");

const processedImage = document.getElementById("processedImage");
const resultMessage = document.getElementById("resultMessage");

// Upload an image
imageInput.addEventListener("change", function () {
    const file = this.files[0];

    if (!file) return;

    selectedImage = file;
    displayImage(URL.createObjectURL(file));
});

// Select a sample image
async function selectSample(filename) {
    try {
        const response = await fetch("assets/" + filename);

        if (!response.ok) {
            throw new Error("Could not load " + filename);
        }

        const blob = await response.blob();

        selectedImage = new File(
            [blob],
            filename,
            { type: blob.type }
        );

        displayImage(URL.createObjectURL(blob));

    } catch (error) {
        alert(error.message);
    }
}

// Display original image
function displayImage(imageURL) {
    originalImage.src = imageURL;
    originalImage.style.display = "block";
    previewMessage.style.display = "none";

    // Clear previous result
    processedImage.style.display = "none";
    resultMessage.style.display = "block";
    resultMessage.textContent = "Choose an operation to process this image.";

    console.log("Selected image:", selectedImage.name);
}

// Update slider values
document.getElementById("minIntensity").addEventListener("input", function () {
    document.getElementById("minValue").textContent = this.value;
});

document.getElementById("maxIntensity").addEventListener("input", function () {
    document.getElementById("maxValue").textContent = this.value;
});

document.getElementById("gammaValue").addEventListener("input", function () {
    document.getElementById("gammaDisplay").textContent = this.value;
});

// Send image to Python backend
async function processImage(operation) {

    if (!selectedImage) {
        alert("Please upload or select an image first.");
        return;
    }

    const formData = new FormData();

    formData.append("image", selectedImage);
    formData.append("operation", operation);

    if (operation === "contrast") {
        formData.append(
            "min_intensity",
            document.getElementById("minIntensity").value
        );

        formData.append(
            "max_intensity",
            document.getElementById("maxIntensity").value
        );
    }

    if (operation === "gamma") {
        formData.append(
            "gamma",
            document.getElementById("gammaValue").value
        );
    }

    if (operation === "smoothing") {
        formData.append(
            "filter_size",
            document.getElementById("filterSize").value
        );
    }

    resultMessage.style.display = "block";
    resultMessage.textContent = "Processing image...";

   try {
    const response = await fetch("https://imageiq-1.onrender.com/process", {
        method: "POST",
        body: formData
    });

       
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Processing failed");
        }

        processedImage.src = "data:image/png;base64," + data.image;
processedImage.style.display = "block";

resultMessage.textContent =
    "Processing completed successfully!";

// Display image quality metrics
document.getElementById("mseValue").textContent =
    data.metrics.mse;

document.getElementById("psnrValue").textContent =
    data.metrics.psnr === "Infinity"
        ? "Infinity"
        : data.metrics.psnr + " dB";

document.getElementById("ssimValue").textContent =
    data.metrics.ssim;
// Display histogram comparison
const labels = Array.from({ length: 256 }, (_, i) => i);

if (originalChart) {
    originalChart.destroy();
}

if (processedChart) {
    processedChart.destroy();
}

// Original image histogram
originalChart = new Chart(
    document.getElementById("originalHistogram"),
    {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Pixel Intensity",
                data: data.original_histogram,
                borderColor: "#7655c9",
                backgroundColor: "rgba(118, 85, 201, 0.15)",
                fill: true,
                pointRadius: 0,
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Pixel Intensity (0–255)"
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Pixel Frequency"
                    },
                    beginAtZero: true
                }
            }
        }
    }
);

// Enhanced image histogram
processedChart = new Chart(
    document.getElementById("processedHistogram"),
    {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Pixel Intensity",
                data: data.processed_histogram,
                borderColor: "#d17b57",
                backgroundColor: "rgba(209, 123, 87, 0.15)",
                fill: true,
                pointRadius: 0,
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Pixel Intensity (0–255)"
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Pixel Frequency"
                    },
                    beginAtZero: true
                }
            }
        }
    }
);

// Generate processing analysis
const analysisText = document.getElementById("analysisText");

const mse = Number(data.metrics.mse);
const psnr = data.metrics.psnr === "Infinity"
    ? Infinity
    : Number(data.metrics.psnr);

const ssim = Number(data.metrics.ssim);

let explanation = "";

if (operation === "contrast") {
    explanation = "Contrast stretching expands the intensity range of the image. ";

    if (ssim > 0.8) {
        explanation += "The image retains much of its original structure while contrast is adjusted.";
    } else {
        explanation += "The structural similarity has decreased noticeably, so some image details or intensity relationships may have changed.";
    }
}

else if (operation === "gamma") {
    explanation = "Gamma correction changes image brightness using a nonlinear intensity transformation. ";

    if (Number(document.getElementById("gammaValue").value) > 1) {
        explanation += "The selected gamma value brightens the image and may reveal details in darker regions.";
    } else {
        explanation += "The selected gamma value darkens the image and may make bright regions easier to inspect.";
    }
}

else if (operation === "smoothing") {
    const size = document.getElementById("filterSize").value;

    explanation = "Gaussian smoothing with a " + size + " × " + size +
        " kernel reduces high-frequency variations and noise. ";

    if (size >= 7) {
        explanation += "The larger kernel produces stronger smoothing but may blur fine details.";
    } else {
        explanation += "The smaller kernel provides moderate smoothing while generally preserving more fine details.";
    }
}

explanation += " MSE: " + mse +
    ", PSNR: " + (psnr === Infinity ? "Infinity" : psnr.toFixed(2) + " dB") +
    ", SSIM: " + ssim + ".";

analysisText.textContent = explanation;


        console.log("Processing result:", data);

    } catch (error) {
        resultMessage.textContent = "Error: " + error.message;
        console.error(error);
    }
}

function resetExperiment() {

    selectedImage = null;

    imageInput.value = "";

    originalImage.src = "";
    originalImage.style.display = "none";
    previewMessage.style.display = "block";

    processedImage.src = "";
    processedImage.style.display = "none";

    resultMessage.textContent =
        "Your enhanced image will appear here.";

    document.getElementById("mseValue").textContent = "--";
    document.getElementById("psnrValue").textContent = "--";
    document.getElementById("ssimValue").textContent = "--";

    document.getElementById("analysisText").textContent =
        "Apply an image-processing operation to see the analysis.";

    if (originalChart) {
        originalChart.destroy();
        originalChart = null;
    }

    if (processedChart) {
        processedChart.destroy();
        processedChart = null;
    }

    document.getElementById("minIntensity").value = 30;
    document.getElementById("maxIntensity").value = 220;
    document.getElementById("gammaValue").value = 1;
    document.getElementById("filterSize").value = 3;

    document.getElementById("minValue").textContent = "30";
    document.getElementById("maxValue").textContent = "220";
    document.getElementById("gammaDisplay").textContent = "1.0";
}

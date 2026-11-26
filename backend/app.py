
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from skimage.feature import hog
import io
print("IMAGEIQ BACKEND FILE LOADED")
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://nayakveda84.github.io"]
    }
})
# ================= EXPERIMENT 4: DIGIT RECOGNITION =================

# Load handwritten digit dataset (0-9)
digit_dataset = load_digits()

X_digits = digit_dataset.images
y_digits = digit_dataset.target

# Split dataset into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X_digits,
    y_digits,
    test_size=0.20,
    random_state=42,
    stratify=y_digits
)

# Model 1: Hu Moments descriptor
def hu_features(images):
    features = []

    for image in images:
        image = cv2.resize(image, (32, 32))
        image = np.uint8(image * (255 / max(image.max(), 1)))

        moments = cv2.moments(image)
        hu = cv2.HuMoments(moments).flatten()

        hu = -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)
        features.append(hu)

    return np.array(features)


# Model 2: HOG descriptor
def hog_features(images):
    features = []

    for image in images:
        feature = hog(
            image,
            orientations=9,
            pixels_per_cell=(2, 2),
            cells_per_block=(2, 2),
            feature_vector=True
        )
        features.append(feature)

    return np.array(features)


# Model 3: Regional (Zoning) descriptor
def zoning_features(images):
    features = []

    for image in images:
        image = cv2.resize(image, (8, 8))
        feature = image.flatten()
        features.append(feature)

    return np.array(features)


# Train and evaluate three separate classifiers
digit_models = {}

for name, extractor in [
    ("Hu Moments", hu_features),
    ("HOG", hog_features),
    ("Regional Zoning", zoning_features)
]:
    train_features = extractor(X_train)
    test_features = extractor(X_test)

    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(train_features, y_train)

    predictions = model.predict(test_features)

    digit_models[name] = {
        "model": model,
        "extractor": extractor,
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test, predictions, average="macro", zero_division=0
        ),
        "recall": recall_score(
            y_test, predictions, average="macro", zero_division=0
        )
    }

print("Experiment 4: Digit recognition models trained successfully.")

# Calculate image quality metrics
def calculate_metrics(original, processed):

    original_gray = cv2.cvtColor(
        original, cv2.COLOR_BGR2GRAY
    )

    processed_gray = cv2.cvtColor(
        processed, cv2.COLOR_BGR2GRAY
    )

    original_float = original_gray.astype(np.float64)
    processed_float = processed_gray.astype(np.float64)

    # Mean Squared Error
    mse = np.mean((original_float - processed_float) ** 2)

    # Peak Signal-to-Noise Ratio
    if mse == 0:
        psnr = float("inf")
    else:
        psnr = 10 * np.log10((255 ** 2) / mse)

    # Structural Similarity Index
    img1 = original_float
    img2 = processed_float

    mu1 = cv2.GaussianBlur(img1, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(img2, (11, 11), 1.5)

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = cv2.GaussianBlur(img1 * img1, (11, 11), 1.5) - mu1_sq
    sigma2_sq = cv2.GaussianBlur(img2 * img2, (11, 11), 1.5) - mu2_sq
    sigma12 = cv2.GaussianBlur(img1 * img2, (11, 11), 1.5) - mu1_mu2

    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2

    ssim_map = (
        (2 * mu1_mu2 + c1) * (2 * sigma12 + c2)
    ) / (
        (mu1_sq + mu2_sq + c1) *
        (sigma1_sq + sigma2_sq + c2)
    )

    ssim = np.mean(ssim_map)

    return {
        "mse": round(float(mse), 4),
        "psnr": "Infinity" if np.isinf(psnr) else round(float(psnr), 4),
        "ssim": round(float(ssim), 4)
    }


@app.route("/")
def home():
    return jsonify({
        "project": "ImageIQ",
        "message": "Welcome to ImageIQ Digital Image Processing Laboratory!",
        "status": "Backend running successfully",
        "experiments": 4
    })


# Process uploaded image
@app.route("/process", methods=["POST"])
def process_image():

    try:
        if "image" not in request.files:
            return jsonify({"error": "Please select an image"}), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({"error": "No image selected"}), 400

        image_bytes = np.frombuffer(file.read(), np.uint8)
        original = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if original is None:
            return jsonify({"error": "Invalid image file"}), 400

        operation = request.form.get("operation", "")

        # Contrast Stretching
        if operation == "contrast":

            min_value = int(request.form.get("min_intensity", 30))
            max_value = int(request.form.get("max_intensity", 220))

            if min_value >= max_value:
                return jsonify({
                    "error": "Maximum intensity must be greater than minimum intensity"
                }), 400

            processed = np.clip(
                (original.astype(np.float32) - min_value)
                * (255.0 / (max_value - min_value)),
                0, 255
            ).astype(np.uint8)

        # Gamma Correction
        elif operation == "gamma":

            gamma = float(request.form.get("gamma", 1.0))

            if gamma <= 0 or gamma > 5:
                return jsonify({"error": "Gamma must be between 0 and 5"}), 400

            lookup_table = np.array([
                ((i / 255.0) ** (1.0 / gamma)) * 255
                for i in range(256)
            ]).clip(0, 255).astype(np.uint8)

            processed = cv2.LUT(original, lookup_table)

        # Spatial Smoothing
        elif operation == "smoothing":

            filter_size = int(request.form.get("filter_size", 3))

            if filter_size not in [3, 5, 7]:
                return jsonify({"error": "Filter size must be 3, 5 or 7"}), 400

            processed = cv2.GaussianBlur(
                original,
                (filter_size, filter_size),
                0
            )

        else:
            return jsonify({"error": "Unknown processing operation"}), 400

        # Calculate metrics
        metrics = calculate_metrics(original, processed)

        # Calculate grayscale histograms
        original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        processed_gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

        original_histogram = cv2.calcHist(
            [original_gray], [0], None, [256], [0, 256]
        ).flatten().astype(int).tolist()

        processed_histogram = cv2.calcHist(
            [processed_gray], [0], None, [256], [0, 256]
        ).flatten().astype(int).tolist()

        # Convert processed image to PNG and Base64
        success, encoded_image = cv2.imencode(".png", processed)

        if not success:
            return jsonify({"error": "Could not encode processed image"}), 500

        image_base64 = base64.b64encode(
            encoded_image.tobytes()
        ).decode("utf-8")

        return jsonify({
            "image": image_base64,
            "operation": operation,
            "metrics": metrics,
            "original_histogram": original_histogram,
            "processed_histogram": processed_histogram,
            "message": "Image processed successfully"
        })

    except Exception as error:
        return jsonify({"error": str(error)}), 500





@app.route('/process-tophat', methods=['POST'])
def process_tophat():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']
        image_bytes = np.frombuffer(file.read(), np.uint8)
        gray = cv2.imdecode(image_bytes, cv2.IMREAD_GRAYSCALE)

        if gray is None:
            return jsonify({"error": "Invalid image file"}), 400

        kernel_size = int(request.form.get('kernel_size', 3))
        kernel_shape = request.form.get('kernel_shape', 'rectangle')
        threshold_value = int(request.form.get('threshold', 30))

        if kernel_size not in [3, 5, 7]:
            return jsonify({"error": "Invalid kernel size"}), 400

        if not 0 <= threshold_value <= 255:
            return jsonify({"error": "Invalid threshold"}), 400

        shapes = {
            'rectangle': cv2.MORPH_RECT,
            'ellipse': cv2.MORPH_ELLIPSE,
            'cross': cv2.MORPH_CROSS
        }

        if kernel_shape not in shapes:
            return jsonify({"error": "Invalid kernel shape"}), 400

        # Create structuring element
        kernel = cv2.getStructuringElement(
            shapes[kernel_shape],
            (kernel_size, kernel_size)
        )

        # Morphological opening
        opened = cv2.morphologyEx(
            gray, cv2.MORPH_OPEN, kernel
        )

        # White Top-Hat = Original - Opening
        tophat = cv2.subtract(gray, opened)

        # Threshold the Top-Hat result
        _, binary = cv2.threshold(
            tophat,
            threshold_value,
            255,
            cv2.THRESH_BINARY
        )

        # Count connected components
        count_4, labels_4, stats_4, centroids_4 = \
            cv2.connectedComponentsWithStats(binary, connectivity=4)

        count_8, labels_8, stats_8, centroids_8 = \
            cv2.connectedComponentsWithStats(binary, connectivity=8)

        objects_4 = count_4 - 1
        objects_8 = count_8 - 1
        foreground_pixels = int(np.count_nonzero(binary))

        # Convert images to Base64
        def encode_image(image):
            success, buffer = cv2.imencode('.png', image)
            if not success:
                raise ValueError("Could not encode processed image")
            return base64.b64encode(buffer).decode('utf-8')

        analysis = (
            f"A {kernel_size}x{kernel_size} {kernel_shape} structuring "
            f"element was used. Morphological opening removed bright "
            f"details smaller than the structuring element. White Top-Hat "
            f"extracted these details. The threshold produced "
            f"{objects_8} objects and {foreground_pixels} foreground pixels. "
            f"Using 4-connectivity gives {objects_4} components, while "
            f"8-connectivity gives {objects_8} components."
        )

        return jsonify({
            "opened_image": encode_image(opened),
            "tophat_image": encode_image(tophat),
            "binary_image": encode_image(binary),
            "object_count": objects_8,
            "foreground_pixels": foreground_pixels,
            "connectivity": f"4-connected: {objects_4} | 8-connected: {objects_8}",
            "analysis": analysis
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/process-watershed', methods=['POST'])
def process_watershed():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']
        image_bytes = np.frombuffer(file.read(), np.uint8)
        original = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if original is None:
            return jsonify({"error": "Invalid image file"}), 400

        foreground_threshold = float(
            request.form.get('foreground_threshold', 0.40)
        )

        distance_threshold = float(
            request.form.get('distance_threshold', 0.40)
        )

        background_size = int(
            request.form.get('background_size', 5)
        )

        if not 0.05 <= foreground_threshold <= 0.95:
            return jsonify({"error": "Invalid foreground threshold"}), 400

        if not 0.05 <= distance_threshold <= 0.95:
            return jsonify({"error": "Invalid distance threshold"}), 400

        if background_size not in [3, 5, 7, 9]:
            return jsonify({"error": "Invalid background size"}), 400

        # 1. Convert image to grayscale
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

        # 2. Reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 3. Extract fruit foreground using Otsu thresholding
        _, binary = cv2.threshold(
            blurred,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        # Automatically correct polarity if background is mostly white
        if np.mean(binary) > 127:
            binary = cv2.bitwise_not(binary)

        # 4. Morphological opening removes small noise
        kernel = np.ones((3, 3), np.uint8)

        opening = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            kernel,
            iterations=2
        )

        # 5. Determine sure background
        dilation_kernel = np.ones(
            (background_size, background_size), np.uint8
        )

        sure_background = cv2.dilate(
            opening,
            dilation_kernel,
            iterations=3
        )

        # 6. Distance transform
        distance = cv2.distanceTransform(
            opening,
            cv2.DIST_L2,
            5
        )

        # 7. Generate sure foreground markers
        max_distance = float(distance.max())

        if max_distance <= 0:
            return jsonify({
                "error": "No fruit foreground detected. Try another image."
            }), 400

        _, sure_foreground = cv2.threshold(
            distance,
            distance_threshold * max_distance,
            255,
            cv2.THRESH_BINARY
        )

        sure_foreground = np.uint8(sure_foreground)

        # 8. Unknown region
        unknown = cv2.subtract(
            sure_background,
            sure_foreground
        )

        # 9. Connected component markers
        marker_count, markers = cv2.connectedComponents(
            sure_foreground
        )

        markers = markers + 1
        markers[unknown == 255] = 0

        marker_visual = cv2.normalize(
            markers.astype(np.float32),
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        # 10. Apply marker-controlled watershed
        markers = cv2.watershed(original.copy(), markers)

        # 11. Draw watershed boundaries in red
        segmented = original.copy()
        segmented[markers == -1] = [0, 0, 255]

        # Count detected fruit regions
        fruit_labels = np.unique(markers)
        fruit_labels = fruit_labels[
            (fruit_labels > 1)
        ]

        fruit_count = len(fruit_labels)

        foreground_pixels = int(
            np.count_nonzero(opening)
        )

        region_count = fruit_count

        # 12. Convert images to Base64
        def encode_image(image):
            success, buffer = cv2.imencode('.png', image)

            if not success:
                raise ValueError("Image encoding failed")

            return base64.b64encode(
                buffer.tobytes()
            ).decode('utf-8')

        # Distance transform visualization
        distance_visual = cv2.normalize(
            distance,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        analysis = (
            f"Watershed detected {fruit_count} foreground regions. "
            f"The image was converted to grayscale, denoised and "
            f"thresholded. Distance transform generated foreground "
            f"markers, and watershed identified boundaries between "
            f"touching regions. Foreground threshold: "
            f"{foreground_threshold:.2f}; distance threshold: "
            f"{distance_threshold:.2f}; background kernel: "
            f"{background_size}x{background_size}. "
            f"Accuracy may decrease with poor lighting, noise and "
            f"heavy fruit overlap. The estimated region count should "
            f"be checked visually."
        )

        return jsonify({
            "original_image": encode_image(original),
            "preprocessed_image": encode_image(opening),
            "distance_image": encode_image(distance_visual),
            "marker_image": encode_image(marker_visual),
            "segmented_image": encode_image(segmented),
            "fruit_count": fruit_count,
            "foreground_pixels": foreground_pixels,
            "region_count": region_count,
            "analysis": analysis
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= EXPERIMENT 4: DIGIT RECOGNITION =================

# ================= EXPERIMENT 4 ROUTES =================

@app.route('/digit-sample/<int:digit>', methods=['GET'])
def digit_sample(digit):
    if digit < 0 or digit > 9:
        return jsonify({"error": "Digit must be between 0 and 9"}), 400

    sample_index = np.where(y_digits == digit)[0][0]
    sample = digit_dataset.images[sample_index]

    sample = np.uint8(sample * (255 / max(sample.max(), 1)))
    sample = cv2.resize(sample, (160, 160), interpolation=cv2.INTER_NEAREST)

    success, buffer = cv2.imencode('.png', sample)

    if not success:
        return jsonify({"error": "Could not encode sample"}), 500

    return send_file(
        io.BytesIO(buffer.tobytes()),
        mimetype='image/png'
    )


@app.route('/process-digit', methods=['POST'])
def process_digit():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "Please upload an image"}), 400

        file = request.files['image']

        if file.filename == "":
            return jsonify({"error": "No image selected"}), 400

        # 1. Read uploaded image
        image_bytes = np.frombuffer(file.read(), np.uint8)
        original = cv2.imdecode(image_bytes, cv2.IMREAD_GRAYSCALE)

        if original is None:
            return jsonify({"error": "Invalid image"}), 400

        # 2. Resize very large images for processing
        height, width = original.shape
        if max(height, width) > 1200:
            scale = 1200 / max(height, width)
            original = cv2.resize(
                original,
                (int(width * scale), int(height * scale))
            )

        # 3. Reduce noise
        blurred = cv2.GaussianBlur(original, (5, 5), 0)

        # 4. Detect whether the background is light or dark
        border_pixels = np.concatenate([
            blurred[0, :],
            blurred[-1, :],
            blurred[:, 0],
            blurred[:, -1]
        ])

        # Black digit on white background -> invert threshold
        if np.mean(border_pixels) > 127:
            _, binary = cv2.threshold(
                blurred, 0, 255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
        else:
            _, binary = cv2.threshold(
                blurred, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

        # 5. Remove tiny noise components
        count, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary, 8
        )

        clean = np.zeros_like(binary)

        for i in range(1, count):
            area = stats[i, cv2.CC_STAT_AREA]

            if area >= 3:
                clean[labels == i] = 255

        # 6. Find digit boundaries
        coords = cv2.findNonZero(clean)

        if coords is None:
            return jsonify({
                "error": "No digit detected. Please upload a clearer digit image."
            }), 400

        x, y, w, h = cv2.boundingRect(coords)

        # 7. Crop the digit
        cropped = clean[y:y+h, x:x+w]

        # 8. Fit digit inside a 20x20 area
        digit_height, digit_width = cropped.shape

        scale = 20.0 / max(digit_height, digit_width)

        new_width = max(1, int(digit_width * scale))
        new_height = max(1, int(digit_height * scale))

        digit_resized = cv2.resize(
            cropped,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

        # 9. Place digit in a 28x28 black canvas
        canvas = np.zeros((28, 28), dtype=np.uint8)

        offset_x = (28 - new_width) // 2
        offset_y = (28 - new_height) // 2

        canvas[
            offset_y:offset_y + new_height,
            offset_x:offset_x + new_width
        ] = digit_resized

        # 10. Prepare 8x8 image for sklearn digit models
        resized = cv2.resize(
            canvas,
            (8, 8),
            interpolation=cv2.INTER_AREA
        )

        processed = np.round(
            resized.astype(np.float32) * (16.0 / 255.0)
        ).astype(np.float32)

        sample = np.array([processed])

        # 11. Predict using all three descriptors
        predictions = {}

        for name, details in digit_models.items():
            features = details["extractor"](sample)

            predictions[name] = int(
                details["model"].predict(features)[0]
            )

        predicted_digit = predictions["HOG"]

        # 12. Create enlarged preprocessed visualization
        display_image = cv2.resize(
            canvas,
            (160, 160),
            interpolation=cv2.INTER_NEAREST
        )

        # 13. Boundary representation
        contours, _ = cv2.findContours(
            display_image.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        boundary = cv2.cvtColor(
            display_image,
            cv2.COLOR_GRAY2BGR
        )

        cv2.drawContours(
            boundary,
            contours,
            -1,
            (0, 0, 255),
            2
        )

        # 14. Regional zoning representation
        regional = cv2.cvtColor(
            display_image,
            cv2.COLOR_GRAY2BGR
        )

        for position in [40, 80, 120]:
            cv2.line(
                regional,
                (position, 0),
                (position, 160),
                (0, 255, 0),
                1
            )

            cv2.line(
                regional,
                (0, position),
                (160, position),
                (0, 255, 0),
                1
            )

        # 15. Encode images
        def encode_image(image):
            success, buffer = cv2.imencode('.png', image)

            if not success:
                raise ValueError("Image encoding failed")

            return base64.b64encode(
                buffer.tobytes()
            ).decode('utf-8')

        preprocessed_base64 = encode_image(display_image)
        boundary_base64 = encode_image(boundary)
        regional_base64 = encode_image(regional)

        # 16. Descriptor comparison
        comparison = (
            "<table>"
            "<tr><th>Descriptor</th>"
            "<th>Prediction</th><th>Accuracy</th></tr>"
        )

        for name, details in digit_models.items():
            comparison += (
                f"<tr><td>{name}</td>"
                f"<td>{predictions[name]}</td>"
                f"<td>{details['accuracy'] * 100:.2f}%</td></tr>"
            )

        comparison += "</table>"

        # 17. Evaluation
        evaluation = (
            f"<p>Dataset: {len(digit_dataset.target)} "
            "handwritten digit images.</p>"
            f"<p>Training samples: {len(X_train)} | "
            f"Testing samples: {len(X_test)}</p>"
        )

        for name, details in digit_models.items():
            evaluation += (
                f"<p><b>{name}</b> — "
                f"Accuracy: {details['accuracy'] * 100:.2f}% | "
                f"Precision: {details['precision'] * 100:.2f}% | "
                f"Recall: {details['recall'] * 100:.2f}%</p>"
            )

        # 18. Analysis
        analysis = (
            f"The uploaded digit was classified as {predicted_digit} "
            "using the HOG descriptor. "
            f"Hu Moments predicted {predictions['Hu Moments']}, "
            f"while Regional Zoning predicted "
            f"{predictions['Regional Zoning']}. "
            "The image was binarized, cropped, centered and normalized "
            "before feature extraction. "
            "Recognition may vary depending on handwriting style "
            "and image quality."
        )

        print("Preprocessed image length:", len(preprocessed_base64))
        print("Boundary image length:", len(boundary_base64))
        print("Regional image length:", len(regional_base64))
        print("Predicted digit:", predicted_digit)

        # 19. Return results
        return jsonify({
            "preprocessed_image": preprocessed_base64,
            "boundary_image": boundary_base64,
            "regional_image": regional_base64,
            "predicted_digit": predicted_digit,
            "analysis": analysis,
            "descriptor_comparison": comparison,
            "evaluation": evaluation
        })

    except Exception as e:
        print("Digit processing error:", str(e))
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)
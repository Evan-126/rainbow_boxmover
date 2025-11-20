import cv2

# Initialize video capture object for the virtual camera.
# The index '0' typically refers to the default webcam.
# If you have multiple cameras (physical and virtual),
# you might need to try different indices (0, 1, 2, etc.)
# to find the correct one for Camo.
cap = cv2.VideoCapture(1)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video stream from Camo.")
    exit()

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # If frame is not read successfully, break the loop
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Display the captured frame
    cv2.imshow('Camo Cam Feed', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and destroy all windows
cap.release()
cv2.destroyAllWindows()

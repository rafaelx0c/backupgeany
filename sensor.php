<?php
// Define the path to the Python script
$pythonScriptPath = '/path/to/read_sensor.py';

// Construct the command to run the Python script
$command = escapeshellcmd("python3 $pythonScriptPath");

// Execute the command and capture the output and errors
$output = shell_exec($command);
if ($output === null) {
    $distance = "Error: Unable to execute the Python script.";
} else {
    $distance = trim($output);
}

// Handle empty or unexpected output
if (empty($distance) || !is_numeric($distance)) {
    $distance = "Error: Invalid or empty output from the Python script.";
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HC-SR04 Sensor Data</title>
    <script src="script.js" defer></script>
</head>
<body>
    <h1>HC-SR04 Sensor Data</h1>
    <p>Distance: <?php echo htmlspecialchars($distance); ?> cm</p>
</body>
</html>

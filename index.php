<?php
$servername = 'localhost';
$username = 'root';
$password = 'root';
$dbname = 'jwt_extract';

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die('Connection failed: ' . $conn->connect_error);
}

$jwt = !empty($_GET['jwt']) ? $_GET['jwt'] : 'unset';

if ($jwt !== 'unset') {
    // sql injection
    $sql = "SELECT id FROM main WHERE jwt='$jwt'";
}
else {
    $sql = 'SELECT * FROM main';
}
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = mysqli_fetch_assoc($result)) {
        echo '$_GET[\'jwt\']: ' . $jwt . ' - id: ' . $row['id'] . '<br>' . PHP_EOL;
    }
} else {
    echo 'No results';
}
$conn->close();

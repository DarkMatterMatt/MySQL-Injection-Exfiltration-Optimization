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

$jwt = !empty($_GET['jwt']) ? "jwt='$_GET[jwt]'" : '';
$id = !empty($_GET['id']) ? "id='$_GET[id]'" : '';

if ($jwt && $id) {
    // sql injection
    $sql = "SELECT jwt, id FROM main WHERE ($jwt) AND ($id)";
}
else if ($jwt || $id) {
    // sql injection
    $sql = "SELECT jwt, id FROM main WHERE $jwt $id";
}
else {
    $sql = 'SELECT * FROM main';
}
echo $sql . '<br>' . PHP_EOL;
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = mysqli_fetch_assoc($result)) {
        echo 'jwt=' . $row['jwt'] . '; id=' . $row['id'] . '<br>' . PHP_EOL;
    }
} else {
    echo 'No results';
}
$conn->close();

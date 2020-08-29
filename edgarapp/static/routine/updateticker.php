<?php
  // Connect to mysql database
  include 'DB.php';

  // connect
  $mysqli = new mysqli($host,$user,$pass,$databaseName);
  $result = $mysqli -> query("SELECT ticker, name FROM $tableName");
  
  while ($row = $result -> fetch_assoc()) {
    $data[] = $row;
  }

  // write to json file
  $fp = fopen('../bootstrap/js/tickers.json', 'w');
  fwrite($fp, json_encode($data));
  fclose($fp);

  $mysqli -> close();

?>
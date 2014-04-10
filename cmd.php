<?php
	$cmd = "python ./sql.py";

	$streams = array(
		0=>array("pipe","r"), // read
		1=>array("pipe","w"), // write
		2=>array("pipe","w")  // stderr
		);

	flush();
	$process = proc_open($cmd, $streams, $pipes, realpath("./"), array());
	$row_cnt = 0;
	$index_cnt = 10;
	$php_array = array();
	$php_array1 = array();

	if (is_resource($process))
	{
		while (($results = fgets($pipes[1])))// && ($row_cnt < 10))
		{
			//$pieces = explode(" ", $results);
			//print_r($results);
			$test = $results;
			echo "<p>$test</p>";
			flush();
			$row_cnt++;
		}
	}
?>
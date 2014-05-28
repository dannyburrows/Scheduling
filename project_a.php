<!DOCTYPE html>

<html lang='en'>
	<head>
		<title>Project A</title>
		<link rel='stylesheet' type='text/css' href ='css/project_a.css'>
		<meta charset='UTF-8'>
		<script type='text/javascript' src='js/Chart.min.js'></script>
	</head>

	<body>

<p>@2014-04-07 18:07:22 - Running maximum subarray function. Please wait while algorithms run. Click on chart to change scale.<table><tr><td></td><td class='algorithm_1'>Algorithm 1 (&mu;s)</td><td class='algorithm_2'>Algorithm 2 (&mu;s)</td><td class='algorithm_3'>Algorithm 3 (&mu;s)</td></tr><tr><td>100</td><td>24</td><td>1</td><td>38</td></tr><tr><td>200</td><td>89</td><td>1</td><td>104</td></tr><tr><td>300</td><td>198</td><td>1</td><td>216</td></tr><tr><td>400</td><td>355</td><td>2</td><td>321</td></tr><tr><td>500</td><td>567</td><td>3</td><td>412</td></tr><tr><td>600</td><td>809</td><td>3</td><td>639</td></tr><tr><td>700</td><td>1104</td><td>3</td><td>779</td></tr><tr><td>800</td><td>1423</td><td>4</td><td>969</td></tr><tr><td>900</td><td>1794</td><td>4</td><td>1118</td></tr><tr><td>1000</td><td>2234</td><td>5</td><td>1250</td></tr><tr><td>2000</td><td>9372</td><td>13</td><td>5348</td></tr><tr><td>3000</td><td>20374</td><td>17</td><td>7760</td></tr><tr><td>4000</td><td>35190</td><td>21</td><td>11068</td></tr><tr><td>5000</td><td>55004</td><td>27</td><td>17827</td></tr><tr><td>6000</td><td>78889</td><td>33</td><td>23576</td></tr><tr><td>7000</td><td>107253</td><td>38</td><td>29004</td></tr><tr><td>8000</td><td>145920</td><td>44</td><td>33405</td></tr><tr><td>9000</td><td>178316</td><td>50</td><td>44211</td></tr></table>
<div id="chart_canvas_outer">
<canvas id="myChart" width="640" height="440">
<div id="chart_canvas">
	<script type="text/javascript">
		var ctx = document.getElementById("myChart").getContext("2d");
		var js_array = ["100","200","300","400","500","600","700","800","900","1000","2000","3000","4000","5000","6000","7000","8000","9000"];
		// filtering out data points 200-900 in each array for now
		js_array = (js_array.slice(0,1)).concat(js_array.slice(9, 18));
		var js_array1 = ["24","89","198","355","567","809","1104","1423","1794","2234","9372","20374","35190","55004","78889","107253","145920","178316"];
		js_array1 = (js_array1.slice(0,1)).concat(js_array1.slice(9, 18));
		var js_array2 = ["1","1","1","2","3","3","3","4","4","5","13","17","21","27","33","38","44","50"];
		js_array2 = (js_array2.slice(0,1)).concat(js_array2.slice(9, 18));
		var js_array3 = ["38","104","216","321","412","639","779","969","1118","1250","5348","7760","11068","17827","23576","29004","33405","44211"];
		js_array3 = (js_array3.slice(0,1)).concat(js_array3.slice(9, 18));


	    var data = {
			labels : js_array,
			datasets : [
				{
					fillColor : "rgba(120,220,220,0.5)",
					strokeColor : "rgba(120,220,220,1)",
					pointColor : "rgba(120,220,220,1)",
					pointStrokeColor : "#fff",
					data : js_array1
				},
				{
					fillColor : "rgba(255,102,51,0.5)",
					strokeColor : "rgba(255,102,51,1)",
					pointColor : "rgba(255,102,51,1)",
					pointStrokeColor : "#fff",
					data : js_array3
				},
				{
					fillColor : "rgba(151,187,205,0.5)",
					strokeColor : "rgba(151,187,205,1)",
					pointColor : "rgba(151,187,205,1)",
					pointStrokeColor : "#fff",
					data : js_array2
				}			
			]
		}

		var options = {
			scaleOverride : true,
			scaleSteps : 10,
			// this should be max of maxes instead of hard coded
			scaleStepWidth : Math.floor((Math.max.apply(Math, js_array1)/10)),
			scaleStartValue : 0,
			bezierCurve : false
		};

		// draw chart
		var maxSubChart = new Chart(ctx).Line(data, options);

		document.getElementById("myChart").addEventListener("mousedown", refocusChart, false);

		var chartFocus = 0;
		function refocusChart(event) {
			//canvas_x = event.pageX;
			//canvas_y = event.pageY;
			switch(chartFocus % 3) {
				case 0:
					options.scaleStepWidth = Math.floor((Math.max.apply(Math, js_array2)/10));
					break;
				case 1:
					options.scaleStepWidth = Math.floor((Math.max.apply(Math, js_array3)/10));
					break;
				case 2:
					options.scaleStepWidth = Math.floor((Math.max.apply(Math, js_array1)/10));
					break;					
			}
			
			// clear canvas and redraw chart
			//if (chartFocus === 0)
			//	ctx.clearRect(0, 0, document.getElementById("myChart").width, document.getElementById("myChart").height);
			//else
			//	ctx.clearRect(0, 0, document.body.clientWidth, document.body.clientHeight);
			
			maxSubChart = new Chart(ctx).Line(data, options);

			chartFocus++;
		}

	</script>
	<script src="js/fs_project_a.js" type="text/javascript"></script>
</div>
</canvas>
</div>

	</body>
</html>
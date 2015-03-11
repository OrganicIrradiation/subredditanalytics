<?php
  if(isset($_GET['subreddit'])) {
    if( $_GET["subreddit"] ) {
      $SUBREDDIT = preg_replace("/[^a-zA-Z0-9_-]/", "", $_GET['subreddit']);;
    } else {
      $SUBREDDIT = "SubredditAnalysis";
    }
  } else {
    $SUBREDDIT = "SubredditAnalysis";
  }
  $SUBREDDIT = strtolower($SUBREDDIT);
  
  $contents = file_get_contents("JSON/".htmlspecialchars($SUBREDDIT).".json");
  $json = utf8_encode($contents);
  $jsonData = json_decode($json,true);
?>

<!DOCTYPE html>
<meta charset="utf-8">
<head>
  <link rel="stylesheet" type="text/css" href="style.css">
  <title>/r/<?php echo(htmlspecialchars($SUBREDDIT)) ?> Subreddit Analytics</title>
</head>
<body>
    <div id="bodycontainer">
        <div id='header'><a href='http://www.reddit.com/r/<?php echo(htmlspecialchars($SUBREDDIT)) ?>'>/r/<?php echo(htmlspecialchars($SUBREDDIT)) ?></a> Subreddit Analytics</div>
        <div id="theSVG"></div>
        <table class="center">
          <tr>
              <th></th>
              <th>Subreddit</th>
              <th>Percentage of Users Shared</th>
              <th>Number of Users Shared</th>
              <th>SubredditAnalysis Available</th>
          </tr>
          <?php
            $subreddits = $jsonData{'nodes'};
            
            // Sort the multidimensional array
            usort($subreddits, "custom_sort");
            // Define the custom sort function
            function custom_sort($a,$b) {
                 return $a['nUsers']<$b['nUsers'];
            }
            
            for ($i=0; $i<count($subreddits); $i++) {
              echo('<tr>');
              echo('<td>' . ($i+1) . '.&nbsp;</td>');
              echo('<td><a href="http://www.reddit.com/r/' . $subreddits[$i]{"id"} . '">/r/' . $subreddits[$i]{"id"} . '</a></td>');
              echo('<td>' . round($subreddits[$i]{"nUsers"}/$jsonData{'nUsersTotal'} * 100) . '%</td>');
              echo('<td>' . round($subreddits[$i]{"nUsers"}) . ' of ' . $jsonData{'nUsersTotal'} . '</td>');
              if (file_exists('JSON/'.strtolower($subreddits[$i]{"id"}).'.json')) {
                echo('<td><a href="show.php?subreddit=' . strtolower($subreddits[$i]{"id"}) . '">Yes</a></td>');
              } else {
                echo('<td>No</td>');
              }
              echo('</tr>');
            }
          ?>
        </table>
        <div class='infoBox'>
            <p>This visualization illustrates the top 25 related subreddits for <a href="http://www.reddit.com/r/<?php echo(htmlspecialchars($SUBREDDIT)) ?>">/r/<?php echo(htmlspecialchars($SUBREDDIT)) ?></a>.   A sample of 1000 users contributions were used to generate a measure of the behavior across subreddits.</p>
            <p>How is this visualization generated?  Let's say that we are analyzing some hypothetical Subreddit A.
                <ol>
                <li>A Python bot requests Subreddit A's 1000 newest hot submissions.</li>
                <li>From these requests, it generates a list of submission and comment authors.</li>
                <li>The bot requests 1000 authors' posting histories.
                <ol>
                <li>When an author contributes to another subreddit, say Subreddit B, a node for that subreddit is created.  If that node already exists, its user count is increased.</li>
                <li>If the author contributes to a third subreddit, say Subreddit C, then a link is established (or strengthend) between Subreddits B and C.</li>
                </ol></li>
                </ol>
            </p>
            <p>Therefore, the best way to interpret the graph above is that the sizes of circles (each representing some Subreddit N) are proportional to the number of users from /r/<?php echo(htmlspecialchars($SUBREDDIT)) ?> who also contributed to Subreddit N.  Links between subreddits illustrate contributors from /r/<?php echo(htmlspecialchars($SUBREDDIT)) ?> who post in both Subreddit N and N+1.  The thicker the line between Subreddit N and N+1, the more users posted in both.</p>
            <p>More analyses and discussions can be found in <a href="http://www.reddit.com/r/SubredditAnalytics/">/r/SubredditAnalytics/</a></p>
            <p>This analysis was inspired by the analyses in <a href="http://www.reddit.com/r/SubredditAnalysis/">/r/SubredditAnalysis/</a></p>
        </div>
    </div>
    <p>
        <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
    </p>
    <p>
        Copyright 2014 <a href="http://steven.cholewiak.com">Steven A. Cholewiak</a>
    </p>
    <div id='processTime'>Data processed at: <?php echo(htmlspecialchars($jsonData{'dateProcessed'})) ?></div>
    
    <script src="http://d3js.org/d3.v3.min.js"></script>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <script>
    var width = 512,
        height = 512;
    
    var color = d3.scale.linear()
        .domain([0,1])
        .range(["black", "red"]);
    
    var force = d3.layout.force()
        .charge(function(d) { return -100; })
        .linkStrength(function(d) { return 0.05*Math.pow(d.weightRel,2);})
        .gravity(0.05)
        .size([width, height]);
    
    var svg = d3.select("#theSVG").append("svg")
        .attr("width", width)
        .attr("height", height);
    
    d3.json("JSON/<?php echo(htmlspecialchars($SUBREDDIT)) ?>.json", function(error, json) {
        force
            .nodes(json.nodes)
            .links(json.links)
            .start();
        
        var link = svg.selectAll(".link")
            .data(json.links)
          .enter().append("line")
            .attr("class", "link")
            .style("stroke-width", function(d) { return Math.pow(d.weightRel,2)*5; });
            
        link.append("title")
            .text(function(d) { return 'Shared users: '+d.weight});
        
        var node = svg.selectAll(".node")
            .data(json.nodes)
          .enter().append("g")
            .attr("class", "node")
            .call(force.drag);
            
        node.append("circle")
            .attr("r", function(d) { return d.nUsersRel*20; })
            .style("fill", function(d) { return color(d.nUsersRel); });
        
        node.append("title")
            .text(function(d) { return 'Users shared with /r/<?php echo(htmlspecialchars($SUBREDDIT)) ?>: '+d.nUsers });
        
        node.append("text")
            .attr("dx", 0)
            .attr("dy", function(d) { return d.nUsersRel*20 + 12; })
            .text(function(d) { return d.id });
            
        force.on("tick", function() {
          link.attr("x1", function(d) { return d.source.x; })
              .attr("y1", function(d) { return d.source.y; })
              .attr("x2", function(d) { return d.target.x; })
              .attr("y2", function(d) { return d.target.y; });
          node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
        });
        
        force.on('end', function() {
          console.log('Force ended!');
          });
    });
    </script>
</body>
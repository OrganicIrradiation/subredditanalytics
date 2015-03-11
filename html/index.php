<!DOCTYPE html>
<meta charset="utf-8">
<head>
    <link rel="stylesheet" type="text/css" href="style.css">
    <title>Available Subreddit Analytics</title>
</head>
<body>
    <div id="bodycontainer">
        <div id='header'>Available Subreddit Analytics</div>
        <div class='infoBox' style='text-align:justify; text-justify:inter-word;'>
            <?php
            foreach (glob("JSON/*.json") as $filename) {
                $pattern = '/JSON\/(.*).json/';
                preg_match($pattern, $filename, $matches);
                echo '<a href="show.php?subreddit='.$matches[1].'">'.$matches[1].'</a> &nbsp; ';
            }
            ?>
        </div>

        <div class='infoBox'>
            <p>This is a list of the <a href="http://www.reddit.com/r/SubredditAnalytics">/r/SubredditAnalytics</a> analyses currently available.  These visualizations can be used as a crude illustration of the relationships between subreddits.   User contributions for each subreddit are used to generate a measure of the behavior across subreddits.</p>
            <p>More analyses and discussions can be found in <a href="http://www.reddit.com/r/SubredditAnalytics/">/r/SubredditAnalytics</a></p>
            <p>These analyses was inspired by <a href="http://www.reddit.com/r/SubredditAnalysis/">/r/SubredditAnalysis</a></p>
            </p>
        </div>
    </div>
    <p>
        <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
    </p>
    <p>
        Copyright 2014 <a href="http://steven.cholewiak.com">Steven A. Cholewiak</a>
    </p>
    <div id='processTime'>Data processed at: </div>
</body>
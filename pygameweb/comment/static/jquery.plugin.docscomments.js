$(document).ready(function () {


    /*
    - fix comment addition for module level comment.
    - format dates in a more human readable way.
    X - show user title for each post.
    X - order comments by newest first.
    X - prevent comments from being added multiple times.
    X - add comment button to reference full url.
    X - Add 'add comment' button in, even if there are comments.
    */

    var _comments = {};

    $.getJSON("https://www.pygame.org/docs/ref/docscomments.json", function (data) {
        //console.log(data);

        // newest comment first.
        var sortComments = function (a,b) {
            var x = a.datetimeon;
            var y = b.datetimeon;
            return ((x < y) ? 1 : ((x > y) ? -1 : 0));
        }

        for(var i=0; i < data.length; i+=1) {
            var link = data[i]['link']
            if(typeof _comments[link] === "undefined") {
                _comments[link] = [];
            }
            _comments[link].push(data[i]);
            _comments[link].sort(sortComments);
        }


        var getComments = function (link) {
            return _comments[link];
        };


        // var addCommentHtml = [
        //  '<form action="http://www.pygame.org/docs/ref/comment_new.php" class="addcomment"><input type="hidden" value="',
        //  '" name="link"><input type="submit" value="Add a Comment"></form>'
        // ];
        var showCommentHtml = [
            '<a href="#comment_',
            '" title="show comments" class="commentButton">Comments ',
            '</a><article id="comment_',
            '" class="hidden commentsArticle"></article>'
        ];
        var commentPartHtml = [
            '<section class="commentPart"><header class="commentHeading">',
            '</header>',
            '<pre class="commentContent">',
            '</pre></section>'
        ]

        $('dt.title').each(function (idx, el) {
            var link = $(el).attr('id');
            if (typeof link === "undefined") {
                return;
            }

            // Add "search internet for source code" buttons.
            //var searchButton = $(searchButtonHtml[0] + link + searchButtonHtml[1] + link + searchButtonHtml[2]);
            //$(el).next().append(searchButton);

            // Add show comments buttons.
            var comments = getComments(link);

            // var addCommentButton = $(addCommentHtml[0] + link + addCommentHtml[1]);
            // $(el).next().append(addCommentButton);

            if(typeof comments === "undefined") {
            } else {
                // show comment button.
                //console.log(link)
                var $showCommentButton = $([showCommentHtml[0],
                              link.replace(/\./g, "_"),
                            showCommentHtml[1],
                            comments.length,
                            showCommentHtml[2],
                              link.replace(/\./g, "_"),
                            showCommentHtml[3]
                              ].join(""));
                $(el).next().append($showCommentButton);

                $showCommentButton.click(function () {
                    //console.log('asdf')
                    var $commentSection = $("#comment_" + link.replace(/\./g, "_"));
                    if (!$commentSection.hasClass('hidden')) {
                        // we have already loaded the comments for this part.
                        return;
                    }
                    $commentSection.removeClass("hidden");
                    $.each(comments, function(idx) {
                        console.log(comments[idx])
                        // date + user
                        var userName = comments[idx]['user_title'];
                        if (userName == null) {
                            userName = 'Anonymous';
                        }
                        var commentHeading = comments[idx]['datetimeon'] + " - " + userName;
                        var commentContent= comments[idx]['content'];

                        var $commentPart = $([commentPartHtml[0],
                              commentHeading,
                            commentPartHtml[1],
                            commentPartHtml[2],
                            commentContent,
                            commentPartHtml[3]].join("\n"));
                        $commentSection.append($commentPart);
                    });

                })
            }
        });
    });


    var searchButtonHtml = [
        '<form action="https://github.com/search" method="get" class="addcomment"><input type="hidden" value="',
        '" name="q"><input type="hidden" name="type" value="Code"><input type="hidden" name="l" value="Python" /><input type="submit" value="Search examples for ',
        '"></form>'
    ];

    // Add "search internet for source code" buttons.
    $('dt.title').each(function (idx, el) {
        var link = $(el).attr('id');
        if (typeof link === "undefined") {
            return;
        }
        var searchButton = $(searchButtonHtml[0] + link + ' language:Python' + searchButtonHtml[1] + link + searchButtonHtml[2]);
        $(el).next().append(searchButton);
    });


    var $newsAlert = $('<span></span>');
    $newsAlert.load('/news-alert-view/1', function(html, a) {
        if($newsAlert.find('#docs-header').length) {
            $("    <style>" +
              "    #docs-header {" +
              "        position: fixed;" +
              "        top: 0;" +
              "        left: 0;" +
              "        right: 0;" +
              "        height: auto;" +
              "        text-align: center;" +
              "        color: white;" +
              "        background-color: black;" +
              "        font-size: larger;" +
              "        line-height: 1.5;" +
              "        padding-top: 13px;" +
              "        padding-bottom: 13px;" +
              "        z-index: 999;" +
              "    }" +
              "    #docs-header > a {" +
              "        color: white;" +
              "        text-decoration: none;" +
              "        border-bottom: 1px dotted #999;" +
              "    }" +
              "    .document .header {" +
              "      padding-top: 55px;" +
              "    }" +
              "    </style>").appendTo("head");
            $newsAlert.appendTo('body');
        }
    });

});

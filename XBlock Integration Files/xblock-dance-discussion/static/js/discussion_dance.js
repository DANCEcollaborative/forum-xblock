function discussion_dance(runtime, element)
{
    var max_comment_id = 0;
    var long_poll_toggle = 1;

    $.ajaxSetup({ async: false});
    /*this is needed because otherwise, by the time the request is processed by the server and
    the callback is executed, the javascript has already been executed. Making the call synchronous, will halt execution
    till response is received.
    */

    function get_remote_asset(asset_name)//asset name must include the extension of the asset
    {
        var ret_asset = '';
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'get_remote_asset'),
            data: JSON.stringify({asset: asset_name}),
            success: function(result)
                    {
                        if(result.error == '')
                        {
                            ret_asset = result.asset;
                        }
                        else
                        {
                            alert("Didn't work" + result.error);//should replace this with some form of logging
                        }

                    }
        });
        //alert('asset fetch complete!'); //for some reason this is needed!
        return(ret_asset);

    }

    function get_asset(asset_name)//asset name must include the extension of the asset
    {
        var ret_asset = '';
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'get_asset'),
            data: JSON.stringify({asset: asset_name}),
            success: function(result)
                    {
                        if(result.error == '')
                        {
                            ret_asset = result.asset;
                        }
                        else
                        {
                            alert("Didn't work" + result.error);//should replace this with some form of logging
                        }

                    }
        });
        //alert('asset fetch complete!'); //for some reason this is needed!
        return(ret_asset);

    }

    function get_comment_box_markup(html_asset, new_div_id, new_text_area_id, new_reply_id, comment_object)
    {
        html_asset = html_asset.replace('class="comment-box"', 'id="' + new_div_id + '" class="comment-box"');
        html_asset = html_asset.replace('id="usercomment"', 'id="' + new_text_area_id +'"');
        if(comment_object != null)
        {
            html_asset = html_asset.replace('{comment}', comment_object["comment"]);
        }
        html_asset = html_asset.replace('id="Reply"', 'id="' + new_reply_id +'"');
        return(html_asset);
    }

    function append_comment_box(comment_box_id, comment_object, html_asset)
    {
        if(parseInt(comment_box_id, 10) > max_comment_id)
        {
            max_comment_id = parseInt(comment_box_id, 10);
            var div_id = "comment-box-" + comment_box_id;
            var text_area_id = "usercomment-" + comment_box_id;
            var reply_id = 'Reply-' + comment_box_id;
            html_asset = get_comment_box_markup(html_asset, div_id, text_area_id, reply_id, comment_object);
            if(comment_object["parent_id"] == "-1")
            {
                $('.discussion-dance').append(html_asset);
            }
            else
            {
                $('#comment-box-' + comment_object["parent_id"]).append(html_asset);
                $('#' + div_id).addClass('reply');
            }
            //Attach click event handler to the Reply button
            $(element).find('#' + reply_id).bind('click',function()
                {
                    $('#' + reply_id).hide();
                    //Handling a reply is a little tricky since the id of the reply box should be its id in the database.
                    //I am handling it here by temporarily spawning a reply box and waiting for the long poll update to
                    //construct the hierarchical representation.

                    reply_box = get_remote_asset('https://raw.githubusercontent.com/DANCEcollaborative/collab-xblock/master/xblock-dance-discussion/static/html/reply_box.html');//Should probably fetch all of these and store as globals
                    //rather than make AJAX call each time.

                    long_poll_toggle = 0; //This will stop the recursive long poll calls. This is needed so that the UI
                    //doesn't keep getting updates and removing the reply box, while you are typing.


                    //=================ADD A CANCEL BUTTON TO CANCEL THE REPLY========================


                    reply_box = get_comment_box_markup(reply_box, 'reply-box-' + comment_box_id, 'replycomment-' + comment_box_id, 'replybutton-' + comment_box_id, null);

                    $(element).find("#" + div_id).append(reply_box);
                    $(element).find('#replybutton-' + comment_box_id).bind('click', function(){
                        on_reply_press('replycomment-' + comment_box_id, comment_box_id);
                        $(element).find('#' + 'reply-box-' + comment_box_id).remove();
                        $('#reply-box-' + comment_box_id).remove();
                        long_poll_toggle = 1;
                        $('#' + reply_id).show();
                        long_poll();//Restart the long poll calls
                    });
                }
            );
        }
    }

    function update_ui(db_data)//asset name must include the extension of the asset
    {
        var html_asset = get_remote_asset('https://raw.githubusercontent.com/DANCEcollaborative/collab-xblock/master/xblock-dance-discussion/static/html/comment_box.html');
        for(var comment_id in db_data)
        {
            append_comment_box(comment_id, db_data[comment_id.toString()], html_asset);
        }

    }

    function long_poll()
    {
        if(long_poll_toggle)
        {
            $.ajax({

                type: "POST",
                url: runtime.handlerUrl(element, 'get_db'),
                data: JSON.stringify({comment: "Random"}),
                success: function(result)
                        {
                            if(result.fetch_status == "Success")
                            {
                                db_dict = JSON.parse(result.db_data);//This is now a dictionary keyed on comment id
                                update_ui(db_dict);
                            }
                            else
                            {
                                alert("Didn't work" + result.fetch_status + " with data " + result.db_data);
                            }
                            var delay = 10000;
                            setTimeout(function(){
                                long_poll();
                            }, delay);

                        }
            });
        }
    }

    function on_reply_press(text_area_id, id_parent)
    {

        var jqCommentBox = $(element).find("#" + text_area_id);
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'post_reply'),
            data: JSON.stringify({comment: jqCommentBox.val(), parent_id: id_parent}),
            success: function(result)
                    {
                        if(result.update_status == "Success")
                        {
                            alert("Database updated!");
                        }
                        else
                        {
                            alert("Database not updated! ret_val is " + result.update_status);
                        }
                    }
        });
        long_poll_toggle = 1;
    }


    function on_post_press(text_area_id)
    {

        var jqCommentBox = $(element).find("#" + text_area_id);
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'post_comment'),
            data: JSON.stringify({comment: jqCommentBox.val()}),
            success: function(result)
                    {
                        if(result.update_status == "Success")
                        {
                            alert("Database updated!");
                        }
                        else
                        {
                            alert("Database not updated! ret_val is " + result.update_status);
                        }
                    }
        });
        long_poll_toggle = 1;
    }

    function clear_comment_box(comment_box_id)
    {
        var jqCommentBox = $(element).find("#" + comment_box_id);
        jqCommentBox.val("");
    }

    $(element).find("#Post").bind('click',function()
        {
            on_post_press('usercomment');
            clear_comment_box("usercomment");
        }
    );

    $(element).find("#Clear").bind('click',function()
        {
            clear_comment_box("usercomment");
        }
    );
    long_poll();
}
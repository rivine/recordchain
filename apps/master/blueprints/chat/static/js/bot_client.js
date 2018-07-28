var stringContentGenerate = function (message){
    return `
    <h4>${message}</h4>
    <div class="form-group">
		<input type="text" class="form-control" id="value">
    </div>`
}

var intContentGenerate = function (message){
    return `
    <h4>${message}</h4>
    <div class="form-group">
		<input type="number" class="form-control" id="value">
    </div>`
}

var mdContentGenerate = function (message){
    let converter = new showdown.Converter();
    const htmlContents = converter.makeHtml(message);
    return `${htmlContents}`;
}

var multiChoiceGenerate = function(message, options){
    let choices = ""
    $.each(options, function(id, value){
        choices += `
        <div class="items col-xs-5 col-sm-5 col-md-3 col-lg-3">
            <div class="info-block block-info clearfix">
                <div data-toggle="buttons" class="btn-group bizmoduleselect">
                    <label class="btn btn-default">
                        <div class="bizcontent">
                            <input type="checkbox" name="value[]" autocomplete="off" value="${id}">
                            <span class="glyphicon glyphicon-ok glyphicon-lg"></span>
                            <h5>${value}</h5>
                        </div>
                    </label>
                </div>
            </div>
        </div>`;
    });
    let contents = `
    <h4>${message}</h4>
    <div class="form-group">
        <div class="checkbox-container">${choices}</div>
    </div>`;
    return contents;
}

var singleChoiceGenerate = function(message, options){
    let choices = "";
    const classes = ["primary", "success", "danger", "warning", "info"];
    let i = 0;
    $.each(options, function(id, value){
        choices += `
        <div class="funkyradio-${classes[i]}">
            <input type="radio" name="value" id="${id}" value="${id}"/>
            <label for="${id}">${value}</label>
        </div>`;
        i += 1;
    });
    let contents = `
    <h4>${message}</h4>
    <div class="funkyradio">${choices}</div>`;
    return contents;
}

var addStep = function(){
    const currentStep = $(".f1-steps").children().length + 1;
	const stepTemplate = `
	<div class="f1-step active">
		<div class="f1-step-icon">${currentStep}</div>
	</div>`;
	$(".f1-step:last-child").removeClass("active");
    $(".f1-steps").append(stepTemplate);
}

var generateSlide = function(res) {
    $("#spinner").toggle();
    if (res["error"]) {
        $("#error").html(res['error']);
        $(".btn-submit").attr("disabled", "false");
        $(".form-box").toggle({"duration": 400});
        return
    }
    addStep();
    let contents = "";
    switch(res['cat']){
        case "string_ask":
            contents = stringContentGenerate(res['msg']);
            break;
        case "int_ask":
            contents = intContentGenerate(res['msg']);
            break;
        case "md_show":
            contents = mdContentGenerate(res['msg']);
            break;
        case "multi_choice":
            contents = multiChoiceGenerate(res['msg'], res['options'])
            break;
        case "single_choice":
            contents = singleChoiceGenerate(res['msg'], res['options'])
            break;
    }
	contents = `
        <fieldset>
            <p id="error" class="red"></p>
			${contents}
			<div class="f1-buttons">
				<button type="submit" class="btn btn-submit" required="true">Next</button>
			</div>
		</fieldset>`;
    $("#wizard").html(contents);
    $(".form-box").toggle({"duration": 400});

	$(".btn-submit").on("click", function(ev){
        ev.preventDefault();
        $(this).attr("disabled", "disabled");
		let value="";
		if (["string_ask", "int_ask"].includes(res['cat'])) {
			value = $("#value").val();
        } else if (res['cat'] === "single_choice"){
            value = $("input[name='value']:checked").val();
        } else if (res['cat'] === "multi_choice"){
            values = [];
            $("input[name='value[]']:checked").each( function () {
                values.push($(this).val());
            });
            value = JSON.stringify(values);
        }
        $("#spinner").toggle();
        $(".form-box").toggle({"duration": 400});
		client.chat.work_report(SESSIONID, value);
		client.chat.work_get(SESSIONID).then(function(res){
            res = JSON.parse(res);
            console.log(res);
            generateSlide(res);
		});
	});
}

client.chat.work_get(SESSIONID).then(function(res){
    res = JSON.parse(res);
    console.log(res);
	generateSlide(res);
});

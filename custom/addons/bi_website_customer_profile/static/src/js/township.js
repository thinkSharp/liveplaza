
function getTownshipByState() {

    var states = [];
    var selected = [];
    var unselected = [];
    for (var option of document.getElementById('state_id').options)
    {
//        document.getElementsByName("township_id").style.display = "none";
        states.push(option.value);
        if(option.selected) {
            selected.push(option.value);
            document.getElementById(selected).style.display = "block";
            document.getElementById('township_id').value = "default";
        }
        for (var state of states) {
            if (state != selected)
                document.getElementById(state).style.display = "none" ;
        }

    }
}

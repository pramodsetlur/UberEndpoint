function validate() {
	document.getElementById("amt_message").innerHTML = "";
	document.getElementById("cb_message").innerHTML = "";
	/*
	var c1 = document.forms["addform"]["c1"].checked;
	var c2 = document.forms["addform"]["c2"].checked;
	var c3 = document.forms["addform"]["c3"].checked;
	var c4 = document.forms["addform"]["c4"].checked;
	*/
	var re=/^[0-9]*\.?[0-9]*$/;
	var amt = document.forms["addform"]["amount"].value;
	var error = 0;
	if (!re.test(amt)){
		document.getElementById("amt_message").innerHTML = "Please enter a valid amount";
		error = 1;
	}
	/*
	if (!c1 && !c2 && !c3 && !c4) {
		document.getElementById("cb_message").innerHTML = "Please select at least one checkbox";
		error = 1;
	}
	*/
	if (error == 1) {
		return false;
	} else {
		return true;
	}
}

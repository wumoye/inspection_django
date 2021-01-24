$('#flip').on('click', function(e) {
	e.preventDefault();

	$('#card').toggleClass('flipped');
	$('#login-img').toggleClass('flipped');
});
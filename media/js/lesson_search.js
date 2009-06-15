function lessonsearch_submit() {
	var start_date = $("#id_start_date").val();
	var end_date = $("#id_end_date").val();
	var start_time = $("#id_start_time").val();
	var end_time = $("#id_end_time").val();
	var weekday = $("#id_weekday").val();
	var student = $("#id_student").val();
	var parent = $("#id_parent").val();
	var lesson_status = $("#id_lesson_status").val();
	$("#lessonsearch-results").load(
		"/schedule/lesson/search/?ajax&start_date=" + encodeURIComponent(start_date)
		+ "&end_date=" + encodeURIComponent(end_date)
		+ "&start_time=" + encodeURIComponent(start_time)
		+ "&end_time=" + encodeURIComponent(end_time)
		+ "&weekday=" + encodeURIComponent(weekday)
		+ "&student=" + encodeURIComponent(student)
		+ "&parent=" + encodeURIComponent(parent)
		+ "&lesson_status=" + encodeURIComponent(lesson_status)
		);
		
	return false;
}
	
$(document).ready(function () {
		$("#lessonsearch-form").submit(lessonsearch_submit);
		});
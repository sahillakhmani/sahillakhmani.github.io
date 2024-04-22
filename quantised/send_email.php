<?php
// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get the form fields
    $name = $_POST['user_name'];
    $email = $_POST['user_email'];
    $subject = $_POST['user_subject'];
    $message = $_POST['user_message'];
    
    // Recipient email
    $to = "sahillakhmani2@gmail.com";

    // Email subject
    $email_subject = "New Contact Form Submission: $subject";

    // Email content
    $email_body = "You have received a new message from your website contact form.\n\n".
                  "Here are the details:\n\nName: $name\n\nEmail: $email\n\nMessage:\n$message";

    // Headers
    $headers = "From: $email";

    // Send email
    if (mail($to, $email_subject, $email_body, $headers)) {
        echo "success";
    } else {
        echo "error";
    }
} else {
    // If the form is not submitted, redirect back to the contact page
    header("Location: contact.html");
}
?>

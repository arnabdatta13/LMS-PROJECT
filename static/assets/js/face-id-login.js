
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

const video = document.getElementById('video-element');
const image = document.getElementById('img-element');
const captureBtn = document.getElementById('capture-btn');
const reloadBtn = document.getElementById('reload-btn');
const loginBtn = document.getElementById('login-btn');

reloadBtn.addEventListener('click', () => {
    window.location.reload();
});

loginBtn.classList.add('not-visible')

if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
            const { height, width } = stream.getTracks()[0].getSettings();

            captureBtn.addEventListener('click', (e) => {
                e.preventDefault();
                captureBtn.classList.add('not-visible');
                loginBtn.classList.remove('not-visible');
            
                const track = stream.getVideoTracks()[0];
                const imageCapture = new ImageCapture(track);
                console.log(imageCapture);
            
                imageCapture.takePhoto().then((blob) => {
                    console.log("took photo:", blob);
                    const img = new Image(width, height);
                    img.src = URL.createObjectURL(blob);
                    image.append(img);
            
                    video.classList.add('not-visible');
            
                    const reader = new FileReader();
            
                    reader.readAsDataURL(blob);
                    reader.onloadend = () => {
                        const base64data = reader.result;
                        console.log(base64data);
            
                        const fd = new FormData();
                        fd.append('csrfmiddlewaretoken', csrftoken);
                        fd.append('photo', base64data);
            
                        loginBtn.addEventListener('click', () => {
                            // Perform the login action here
                            console.log('Login button clicked');
                            $.ajax({
                                type: 'POST',
                                url: 'face-id-dologin',
                                enctype: 'multipart/form-data',
                                data: fd,
                                processData: false,
                                contentType: false,
                                success: (resp, status, xhr) => {
                                    console.log(resp);
                                    console.log("Response status code:", xhr.status);
                                    if (xhr.status === 200) {
                                        // Handle success response
                                        console.log("Login successful");
                                        window.location.href = resp.redirect_url; // Redirect to the URL returned by the server
                                    } else {
                                        // Handle other responses
                                        console.log("Received response, but not a success");
                                        if (resp.error) {
                                            // Store the error message in local storage
                                            localStorage.setItem('errorMessage', resp.error);
                                            // Reload the page
                                            window.location.reload();
                                        }
                                    }
                                },
                                error: (xhr, status, error) => {
                                    console.log(xhr);
                                    console.log("Response status code:", xhr.status);
            
                                    if (xhr.status === 400) {
                                        // Parse the response JSON to get the error message
                                        const resp = JSON.parse(xhr.responseText);
                                        if (resp.error) {
                                            // Store the error message in local storage
                                            localStorage.setItem('errorMessage', resp.error);
                                            // Reload the page
                                            window.location.reload();
                                        }
                                    } else {
                                        // Handle other errors
                                        console.log("Received response, but not a bad request");
                                        // You might want to display a generic error message or take other actions
                                    }
                                }
                            });
                        });
                    }
            
                    // Restore the mirroring effect to the video element after capturing the image
                    video.style.transform = 'scaleX(-1)';
                }).catch((error) => {
                    console.log('takePhoto() error: ', error);
                });
            });            
        })
        .catch((error) => {
            console.log("Something went wrong!", error);
        });
}

// Retrieve and display the error message after page reload
window.onload = function () {
    const errorMessage = localStorage.getItem('errorMessage');
    if (errorMessage) {
        const errorMessageElement = document.getElementById('error-message');
        errorMessageElement.textContent = errorMessage;
        errorMessageElement.style.display = 'block';
        // Clear the error message from local storage
        localStorage.removeItem('errorMessage');
    }
};

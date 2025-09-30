// Function that runs once the window is fully loaded
window.onload = function() {
   var savedBaseUrl = localStorage.getItem('apiBaseUrl');
   if (savedBaseUrl) {
       document.getElementById('api-base-url').value = savedBaseUrl;
       loadPosts();
   }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
   var baseUrl = document.getElementById('api-base-url').value;
   localStorage.setItem('apiBaseUrl', baseUrl);

   fetch(baseUrl + '/posts')
       .then(response => response.json())
       .then(data => {
           const postContainer = document.getElementById('post-container');
           postContainer.innerHTML = '';

           data.forEach(post => {
               const postDiv = document.createElement('div');
               postDiv.className = 'post';
               postDiv.innerHTML = `
                   <h2>${post.title}</h2>
                   <p><strong>Author:</strong> ${post.author || "Unknown"}</p>
                   <p><strong>Date:</strong> ${post.date || "N/A"}</p>
                   <p>${post.content}</p>
                   <button onclick="deletePost(${post.id})">Delete</button>
               `;
               postContainer.appendChild(postDiv);
           });
       })
       .catch(error => console.error('Error:', error));
}

// Function to send a POST request to the API to add a new post
function addPost() {
   var baseUrl = document.getElementById('api-base-url').value;
   var postTitle = document.getElementById('post-title').value;
   var postContent = document.getElementById('post-content').value;
   var postAuthor = document.getElementById('post-author').value;
   var postDate = document.getElementById('post-date').value;

   fetch(baseUrl + '/posts', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
           title: postTitle,
           content: postContent,
           author: postAuthor,
           date: postDate
       })
   })
   .then(response => response.json())
   .then(post => {
       console.log('Post added:', post);
       loadPosts();
   })
   .catch(error => console.error('Error:', error));
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
   var baseUrl = document.getElementById('api-base-url').value;

   fetch(baseUrl + '/posts/' + postId, {
       method: 'DELETE'
   })
   .then(response => {
       console.log('Post deleted:', postId);
       loadPosts();
   })
   .catch(error => console.error('Error:', error));
}

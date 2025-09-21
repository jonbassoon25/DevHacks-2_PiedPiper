// auth.js
const express = require('express');
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

const router = express.Router();

// ------------------
// Passport setup
// ------------------
passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: "http://localhost:8000/auth/google/callback"
}, (accessToken, refreshToken, profile, done) => {
    // This is where you can store or process the user profile
    return done(null, profile);
}));

passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));

// ------------------
// OAuth Routes
// ------------------

// Trigger Google login
router.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

// Google callback route
router.get('/auth/google/callback',
    passport.authenticate('google', { failureRedirect: '/login.html' }),
    (req, res) => {
        console.log("Logged in user:", req.user);

        // Send back a tiny HTML page that sets localStorage
        res.send(`
            <script>
              const user = ${JSON.stringify({
                name: req.user.displayName,
                email: req.user.emails?.[0]?.value || '',
                photo: req.user.photos?.[0]?.value || ''
              })};
              localStorage.setItem('az_user', JSON.stringify(user));
              window.location = '/index.html';
            </script>
        `);
    }
);


// Logout route
router.get('/logout', (req, res, next) => {
    req.logout(function(err) {
        if (err) { return next(err); } // handle any potential errors
        res.redirect('/index.html');
    });
});

module.exports = router;

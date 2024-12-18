module.exports = {
    branches: ['main'],
    plugins: [
        ["@semantic-release/commit-analyzer", {
            "preset": "angular",
            "releaseRules": [
                {
                    "release": process.env.RELEASE_TYPE || "patch"
                }
            ]
        }],
        '@semantic-release/git'
    ]
};

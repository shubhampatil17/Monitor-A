var app = angular.module("amazonMonitor", ["ngRoute", "ngAnimate"]).config(['$routeProvider', function ($routeProvider) {
    $routeProvider.
    when('/login', {
        templateUrl: '../static/partials/login.html'
    }).
    when('/homepage', {
        templateUrl: '../static/partials/homepage.html'
    }).
    when('/signup', {
        templateUrl: '../static/partials/signup.html'
    }).
    when('/list-added-products', {
        templateUrl: '../static/partials/productList.html'
    }).
    otherwise({
        redirectTo: '/homepage'
    });

}]).controller("mainController", function ($scope, $http, $location) {

    $scope.isSignUpActive = function () {
        return $location.path() === '/login';
    }

    $scope.isLoginActive = function () {
        return $location.path() === '/signup';
    }

    $scope.isLogoutActive = function () {
        return $location.path() === '/homepage' || $location.path() === '/list-added-products';
    }

    $scope.logoutUser = function () {
        $http({
            method: 'GET',
            url: '/logout'
        }).then(function (response) {
            if (response.data.status) {
                $location.path("/login");
            } else {
                //note : show error
            }
        }, function (error) {
            //note : handle error
            console.log(error);
        })
    }

    $scope.goToLandingPartial = function () {
        $http({
            method: 'GET',
            url: '/checkLoginStatus'
        }).then(function (response) {
            if (response.data.status) {
                $location.path("/homepage");
            } else {
                $location.path("/login");
            }
        }, function (error) {
            //note : handle error
            console.log(error);
        })
    }
    $scope.goToLandingPartial();

}).controller("signupController", function ($scope, $http, $location) {
    $scope.username;
    $scope.email;
    $scope.password;
    $scope.retypepassword;
    $scope.usernameValidityStatus = true;
    $scope.usernameValidityStatusText;
    $scope.checkingUsernameUnderProgress;
    $scope.emailValidityStatus = true;
    $scope.emailValidityStatusText;
    $scope.checkingEmailUnderProgress;
    $scope.signupInProcess = false;


    $scope.checkEmailValidity = function () {
        console.log("called");
        if ($scope.email) {
            $scope.checkingEmailUnderProgress = true;
            $http({
                method: 'POST',
                url: '/checkEmailValidity',
                data: {
                    "email": $scope.email
                }
            }).then(function (response) {
                $scope.checkingEmailUnderProgress = false;
                if (response.data.status) {
                    $scope.emailValidityStatus = true;
                    $scope.emailValidityStatusText = "";
                } else {
                    $scope.emailValidityStatus = false;
                    $scope.emailValidityStatusText = "Already Exist !";
                }
            }, function (error) {
                //handle error here
                console.log(error);
            })
        } else {
            $scope.emailValidityStatus = true;
            $scope.emailValidityStatusText = '';
            $scope.checkingEmailUnderProgress = false;
        }
    }

    $scope.checkUsernameValidity = function () {
        if ($scope.username) {
            $scope.checkingUsernameUnderProgress = true;
            $http({
                method: 'POST',
                url: '/checkUsernameValidity',
                data: {
                    "username": $scope.username
                }
            }).then(function (response) {
                $scope.checkingUsernameUnderProgress = false;
                if (response.data.status) {
                    $scope.usernameValidityStatus = true;
                    $scope.usernameValidityStatusText = "Available !";
                } else {
                    $scope.usernameValidityStatus = false;
                    $scope.usernameValidityStatusText = "Not Available !";
                }
            }, function (error) {
                //handle error here
                console.log(error)
            })

        } else {
            $scope.usernameValidityStatus = true;
            $scope.usernameValidityStatusText = '';
            $scope.checkingUsernameUnderProgress = false;

        }
    }

    $scope.signupUser = function () {
        if ($scope.usernameValidityStatus && $scope.emailValidityStatus && ($scope.password === $scope.retypepassword)) {
            $scope.signupInProcess = true;
            $http({
                method: 'POST',
                url: '/signUpUser',
                data: {
                    "username": $scope.username,
                    "email": $scope.email,
                    "password": $scope.password
                }
            }).then(function (response) {
                $scope.signupInProcess = false;
                if (response.data.status) {
                    $scope.signupSuccess = true;
                } else {
                    $scope.signupFailed = true;
                    $scope.signupFailureMessage = "Something Went wrong ! Please try again later."
                }
            }, function (error) {
                //handle error here
                $scope.signupInProcess = false;
                console.log(error)
            })

        } else {
            $scope.signupFailed = true;
            if ($scope.password !== $scope.retypepassword) {
                $scope.signupFailureMessage = "Password mismatch !"
            } else {
                $scope.signupFailureMessage = "One or more invalid credentials !";
            }
        }
    }

}).controller("loginController", function ($scope, $http, $location, $window) {
    $scope.username;
    $scope.password;
    $scope.loginInProcess = false;

    $scope.startOAuthCycle = function () {
        $http({
            method: 'GET',
            url: '/getOAuthUrl'
        }).then(function (response) {
            if (response.data.status) {
                $window.location.href = response.data.oauth_url;
            } else {
                $location.path("/login");
            }
        }, function (error) {
            //handle error
            console.log(error);
        })
    }

    $scope.checkAccessToken = function () {
        $http({
            method: 'GET',
            url: '/checkAccessTokenValidity',
        }).then(function (response) {
            $scope.loginInProcess = false;
            if (response.data.status) {
                $location.path("/homepage");
            } else {
                $scope.startOAuthCycle();
            }
        }, function (error) {
            //handle error
            console.log(error);
        })
    }

    $scope.checkCredentials = function () {
        $scope.loginInProcess = true;
        $http({
            method: 'POST',
            url: '/login',
            data: {
                "username": $scope.username,
                "password": $scope.password
            }
        }).then(function (response) {
            if (response.data.status) {
                $scope.checkAccessToken();
            } else {
                $scope.loginInProcess = false;
                $scope.loginFailed = true;
                $scope.loginFailureMessage = "Login failed ! Invalid credentials";
            }
        }, function (error) {
            $scope.loginInProcess = false;
            $scope.loginFailed = true;
            $scope.loginFailureMessage = "Something went wrong ! Please try again later.";
        })
    }
}).controller("homeController", function ($scope, $http, $timeout) {
    $scope.product = {};
    $scope.product.intervalUnit = "Seconds";

    $scope.addNewProduct = function () {
        $http({
            method: 'POST',
            url: '/addNewProduct',
            data: {
                "asin": $scope.product.productASIN,
                "interval": $scope.product.interval,
                "intervalUnit": $scope.product.intervalUnit,
                "thresholdPrice": $scope.product.thresholdPrice
            }
        }).then(function (response) {
            $scope.addProductComplete = true;
            $scope.addProductSuccess = response.data.status;
            $scope.addProductCompleteMessage = response.data.message;
            $timeout(function () {
                $scope.addProductComplete = false;
            }, 8000)
        }, function (error) {
            $scope.addProductComplete = true;
            $scope.addProductSuccess = true;
            $scope.addProductCompleteMessage = "Something went wrong ! Please try again later"
            $timeout(function () {
                $scope.addProductComplete = false;
            }, 8000)
        })
    }

    $scope.goToLandingPartial();
}).controller("productListController", function ($scope, $http, $window, $timeout) {
    $scope.productsPerPage = 4;
    $scope.paginationSlot = [1, 2, 3, 4, 5];
    $scope.paginationIndex = 1;

    $scope.rollBackPaginationSlot = function () {
        if ($scope.paginationIndex > 5) {
            for (page in $scope.paginationSlot) {
                $scope.paginationSlot[page] = $scope.paginationSlot[page] - 5;
            }

            $scope.paginationIndex = $scope.paginationSlot[0];
        }
    }

    $scope.rollForwardPaginationSlot = function () {

        if ($scope.ceil($scope.paginationIndex / 5) < $scope.ceil(($scope.productList.length / $scope.productsPerPage) / 5)) {
            for (var page in $scope.paginationSlot) {
                $scope.paginationSlot[page] = $scope.paginationSlot[page] + 5;
            }

            $scope.paginationIndex = $scope.paginationSlot[0];
        }
    }

    $scope.changePaginationIndex = function (page) {
        $scope.paginationIndex = page;
    }

    $scope.getProductList = function () {
        $http({
            method: 'GET',
            url: '/getAddedProducts',
        }).then(function (response) {
            if (response.data.status) {
                $scope.productList = response.data.products;
            }
        }, function (error) {
            //handle error
            console.log(error)
        })
    }

    $scope.floor = function (number) {
        return $window.Math.floor(number);
    }

    $scope.ceil = function (number) {
        return $window.Math.ceil(number);
    }


    $scope.popConfirmationBox = function (asin) {
        $scope.asinToDelete = asin;
        $scope.showDeleteResponse = false;
        $scope.productDeletionSuccess = false;
        $scope.productUnderDeletion = false;
        console.log($('#confirmationModal')[0]);
        $('#confirmationModal').modal('show');
    }

    $scope.deleteProduct = function (asin) {
        $scope.productUnderDeletion = true;
        $http({
            method: 'DELETE',
            url: '/deleteProduct',
            data: {
                'asin': asin
            }
        }).then(function (response) {
            $scope.productDeletionSuccess = response.data.status;
            $scope.deletionResponse = response.data.message;
            $scope.showDeleteResponse = true;

            $timeout(function () {
                $('#confirmationModal').modal('hide');
            }, 3000)
            $scope.getProductList();

        }, function (error) {
            //handle error
            console.log(error)
        })
    }

    $scope.getProductList();
});
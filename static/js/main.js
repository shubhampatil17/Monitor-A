var app = angular.module("amazonMonitor", ["ngRoute"]).config(['$routeProvider', function ($routeProvider) {
    $routeProvider.
    when('/', {
        templateUrl: '../static/partials/homepage.html'
    }).
    when('/signup', {
        templateUrl: '../static/partials/signup.html'
    }).
    when('/list-added-products', {
        templateUrl: '../static/partials/productList.html'
    }).
    otherwise({
        redirectTo: '/'
    });

}]).controller("mainController", function ($scope, $http, $window, $location) {
    $scope.username;
    $scope.password;

    $scope.isSignUpActive = function () {
        return $location.path() !== '/signup';
    }

    $scope.checkLoginStatus = function () {
        $http({
            method: 'GET',
            url: '/checkLoginStatus'
        }).then(function (response) {
            if (response.data.status) {
                $scope.isLoggedInUser = response.data.status;
                $scope.currentUser = response.data.username;
            }
        }, function (error) {
            console.log(error);
            //handle error
        })
    }

    $scope.logoutUser = function () {
        $http({
            method: 'GET',
            url: '/logout'
        }).then(function (response) {
            if (response.data.status) {
                $scope.isLoggedInUser = false;
                $location.path("/");
            } else {
                //note : show error
            }
        }, function (error) {
            //note : handle error
            console.log(error);
        })
    }

    $scope.startOAuthCycle = function () {
        $http({
            method: 'GET',
            url: '/getOAuthUrl'
        }).then(function (response) {
            if (response.data.status) {
                $window.location.href = response.data.oauth_url;
            } else {
                $scope.isLoggedInUser = false;
                $location.path("/");
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
            if (response.data.status) {
                $('#loginModal').modal('hide');
                //$scope.submitProductData();
                $scope.checkLoginStatus();
            } else {
                $scope.startOAuthCycle();
            }
        }, function (error) {
            //handle error
            console.log(error);
        })
    }

    $scope.checkCredentials = function () {
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
                $scope.loginFailed = true;
                $scope.loginFailureMessage = "Login failed ! Invalid credentials";
            }
        }, function (error) {
            $scope.loginFailed = true;
            $scope.loginFailureMessage = "Something went wrong ! Please try again later.";
        })
    }

    $scope.checkLoginStatus();

}).controller("homeController", function ($scope, $http, $timeout, $location, $anchorScroll) {

    $scope.searchKeywords;
    $scope.searchLocale = "co.uk";
    $scope.searchCompleted = false;

    $scope.product = {};
    $scope.product.intervalUnit = "Seconds";
    $scope.product.locale = "co.uk";

    $scope.searchItems = function () {
        if ($scope.searchKeywords) {
            $scope.searchUnderProgress = true;
            $http({
                method: 'GET',
                url: '/searchItems',
                params: {
                    'searchKeywords': $scope.searchKeywords,
                    'searchLocale': $scope.searchLocale
                }
            }).then(function (response) {
                $scope.searchUnderProgress = false;
                $scope.searchCompleted = true;

                angular.element

                if (response.data.status) {
                    $scope.searchResultMessage = response.data.searchResults.length + " warehouse item(s) found";
                    $scope.searchResults = response.data.searchResults;
                } else {
                    $scope.searchResultMessage = "Something went wrong ! Please try again.";
                }

            }, function (error) {
                //handle error;
                console.log(error);
            })
        }
    }

    $scope.popUpAddProductModal = function (asin, locale) {
        $("#addProductModal").modal("show");
        $scope.product.productASIN = asin;
        $scope.product.locale = locale;
    }


    $scope.submitProductData = function () {
        $http({
            method: 'GET',
            url: '/checkLoginStatus'
        }).then(function (response) {
            if (response.data.status) {
                $scope.addNewProduct();
            } else {
                $('#addProductModal').modal('hide');
                $('#loginModal').modal('show');
            }
        }, function (error) {
            console.log(error);
            //log error
        })
    }

    $scope.addNewProduct = function () {
        $http({
            method: 'POST',
            url: '/addNewProduct',
            data: {
                "asin": $scope.product.productASIN,
                "interval": $scope.product.interval,
                "intervalUnit": $scope.product.intervalUnit,
                "thresholdPrice": $scope.product.thresholdPrice,
                "locale": $scope.product.locale
            }
        }).then(function (response) {
            $scope.addProductComplete = true;
            $scope.addProductSuccess = response.data.status;
            $scope.addProductCompleteMessage = response.data.message;
            $scope.product = {};
            $scope.product.intervalUnit = "Seconds";
            $scope.product.locale = "co.uk";
            $timeout(function () {
                $scope.addProductComplete = false;
            }, 8000);
        }, function (error) {
            $scope.addProductComplete = true;
            $scope.addProductSuccess = true;
            $scope.addProductCompleteMessage = "Something went wrong ! Please try again later"
            $timeout(function () {
                $scope.addProductComplete = false;
            }, 8000);
        })
    }

}).controller("signupController", function ($scope, $http) {
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
                    $scope.emailValidityStatusText = "Already exists !";
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
                    $scope.signupFailureMessage = response.data.message;
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

}).controller("productListController", function ($scope, $http, $timeout, $window) {
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
            $scope.fetchProducts();

        }, function (error) {
            //handle error
            console.log(error)
        })
    }

    $scope.fetchProducts = function () {
        if ($scope.isLoggedInUser) {
            $http({
                method: 'GET',
                url: '/getUserProducts'
            }).then(function (response) {
                if (response.data.status) {
                    $scope.productList = response.data.products;
                }

            }, function (error) {
                //handle error
                console.log(error);
            })

        } else {
            $http({
                method: 'GET',
                url: '/getRandomProducts'
            }).then(function (response) {
                if (response.data.status) {
                    $scope.productList = response.data.products;
                }

            }, function (error) {
                //handle error
                console.log(error);
            })
        }
    }

    $scope.$watch('isLoggedInUser', $scope.fetchProducts);
    $scope.fetchProducts();

});
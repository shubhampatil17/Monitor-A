var app = angular.module("amazonMonitor", ["ngRoute"]).config(['$routeProvider', function($routeProvider) {
    $routeProvider.
    when('/', {
        templateUrl : '../static/login.html',
    }).
    when('/addProduct', {
        templateUrl : '../static/homepage.html',
    }).
    otherwise({
        redirectTo : '/'
    });
}]);
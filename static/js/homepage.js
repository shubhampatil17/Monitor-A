var app = angular.module("amazonMonitor", []).controller("mainController", function($scope, $http){
    $scope.product = {
        intervalUnit : 'Seconds'
    }
    
    $scope.addProduct = function(){
        $http({
            url: "/addProduct",
            method: "post",
            data: $scope.product
        }).then(function(response){
            console.log(response);
//            $scope.productSubmissionResponse = response.data;
        }, function(error){
            console.log(error);
//            $scope.productSubmissionResponse = error.data;
        })
    }
    
});
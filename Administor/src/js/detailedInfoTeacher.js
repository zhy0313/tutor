(function(){
  Vue.http.interceptors.push(function(request, next){
    request.credentials = true;
    next();
  });
	var vm = new Vue({
      el: 'body',
      data:{
        domain: 'http://www.yinzishao.cn:8000',
      	status:{
      		isSelecting: true,
	        isLoading: false,
	        isTutorInfo: false,
	        selected: '',
          hot_not:"设为热门",
          isList: false,
          isNoList: true,
          text: '删除该请求',
      	},
      	msgDetailedList:{
          tea_id: '',
      		certificate_photo:'../img/user02.png',
          name:'张先生',
          subject:'数学',
          subject_other:'',
          grade:'高一',
          place:"天河",
          time:"周六上午",
          native_place:"天河",
          teacher_method:"nice,细心",
          teacher_method_other: '',
          expection:"上课要耐心细致",
          sex:'男',
          salary_bottom:20,
          salary_top:60,
          tel:1234567891,
          self_comment:'特别受学生喜欢',
          score: 'GDP棒棒',
          campus_major:'英语',
          teach_show_photo:['../img/user02.png','../img/user02.png','../img/user02.png']
      	},
      	msgList:[
          // {pd_id:0,name:'张先生',isInvited: '已报名',teacher_sex: '不限', learning_phase: '高中',aim:'提高成绩',subject:'数学',subject_other: '',grade:'高一',address:"大学城小洲",time:"周六上午",class_field: '成绩优良',teacher_method:"nice,细心", teacher_method_other: '',require:"",salary: '18/h', bonus: '100/月',deadline:'2017-01-12',tel:'18826103726'},
          // {pd_id:1,name:'张先生',isInvited: '已接受',teacher_sex: '不限', learning_phase: '高中',aim:'提高成绩',subject:'数学',subject_other: '',grade:'高一',address:"大学城小洲",time:"周六上午",class_field: '成绩优良',teacher_method:"nice,细心", teacher_method_other: '',require:"",salary: '18/h', bonus: '100/月',deadline:'2017-01-12',tel:'18826103726'},
          // {pd_id:2,name:'张先生',isInvited: '已拒绝',teacher_sex: '不限', learning_phase: '高中',aim:'提高成绩',subject:'数学',subject_other: '',grade:'高一',address:"大学城小洲",time:"周六上午",class_field: '成绩优良',teacher_method:"nice,细心", teacher_method_other: '',require:"",salary: '18/h', bonus: '100/月',deadline:'2017-01-12',tel:'18826103726'},
          // {pd_id:3,name:'张先生',isInvited: '已报名',teacher_sex: '不限', learning_phase: '高中',aim:'提高成绩',subject:'数学',subject_other: '',grade:'高一',address:"大学城小洲",time:"周六上午",class_field: '成绩优良',teacher_method:"nice,细心", teacher_method_other: '',require:"",salary: '18/h', bonus: '100/月',deadline:'2017-01-12',tel:'18826103726'},
          // {pd_id:4,name:'张先生',isInvited: '已报名',teacher_sex: '不限', learning_phase: '高中',aim:'提高成绩',subject:'数学',subject_other: '',grade:'高一',address:"大学城小洲",time:"周六上午",class_field: '成绩优良',teacher_method:"nice,细心", teacher_method_other: '',require:"",salary: '18/h', bonus: '100/月',deadline:'2017-01-12',tel:'18826103726'},
		    ],
        jsonData: [],
        start: 0,
        id: 0,
      	detailedList: [],
      },
      ready: function(){
          this.getId();
          this.renderTutor();
          this.renderOrderData();
          this.status.isLoading = true;
      },
      methods: {
        down: function(){
          this.start++;
          if(this.jsonData.length!==0){
            this.renderOrderData();
          }
        },
        getId: function(){
          var id = parseInt(this.getParam('listId'));
          this.id = id;
        },
      	renderOrderData: function(){
          this.status.isSelecting = true;
          this.$http.post(this.domain+'/getUserOrders',{
            "id":this.id,
            "user":"teacher",
            "start":this.start,
            "size":6
          },{
            crossOrigin: true,
            headers:{
              'Content-Type':'application/json' 
            }
          }).then(function(res){
            console.log(res.json());
            if(res.json().success == 0){
              console.log(res.json().error);
            }else{
              this.jsonData = res.json();
              var data = res.json();
              if(data.length!=0){
                for(var i = 0;i<data.length;i++){
                  if(data[i].result == '已拒绝'||data[i].result == '家长已拒绝'){
                    data[i].isRed = true;
                  }else{
                    data[i].isRed = false;
                  }
                 }
                var json=this.msgList.concat(res.json());
                this.$set('msgList',json);
                this.status.isSelecting = false;
              }else{
                if(this.msgList.length==0){
                  this.status.isNoList = true;
                  this.status.isList = false;
                }
              }
            }
          });
		    },
        getParam: function(param) {   //获取url上的参数
          var str = location.search;
          if (str.indexOf("?") == -1) return '';
          str = str.substr(1, str.length).split("&");
          for (var i = 0, cell, length = str.length; i < length; i++) {
            cell = str[i].split('=');
            if (cell[0] == param) {
              return cell[1];
            }
          }
          return false;
        },
  	    renderTutor: function(){
  	      this.$http.post(this.domain+'/getInfo',{
              'id': this.id,
              'format': true,
              'user': 'teacher'
            },{
          	crossOrigin: true,
            headers:{
              'Content-Type':'application/json' 
            }
          }).then(function(res){
          	console.log(res.json());
            if(res.json().sucess == 0){
              console.log(res.json().error);
            }else{
              var data = res.json();
              if(data.certificate_photo!=''||data.certificate_photo!=null){
                data.certificate_photo=this.domain+data.certificate_photo;
              }
              var photo=data.teach_show_photo,len = photo.length;
              if(len>0){
               for(var i=0;i<len;i++){
                photo[i]=this.domain+photo[i];
               }
              }
              this.$set('msgDetailedList',data);
              if(this.msgDetailedList.hot_not == 0){
                this.status.hot_not = '设为热门';
              }else{
                this.status.hot_not = '取消热门';
              }
            }
          });
  	    },
        onReturn: function(){
          var searchWord = this.getParam('keyword');
          if(this.getParam('page')=='popularTeacher'){
            window.location.href = './popularTeacher.html?keyword='+searchWord;
          }else{
            window.location.href = './userAdministor.html?user=teacher&keyword='+searchWord;
          }
        },
        onUser:function(){
      		window.location.href = './userAdministor.html';
      	},
      	onDeal: function(){
          window.location.href = './deal.html';
      	},
      	onOther: function(){
          window.location.href = './other.html';
      	},
      	onPopular: function(){
          var popular,msgText;
          if(this.status.hot_not == '设为热门'){
              popular = 1;
              msgText = '取消热门';
          }else{
            popular = 0;
            msgText = '设为热门';
          }
      		this.$http.post(this.domain+'setHot',{
            'id': this.id,
            "type": popular,
            'user': "teacher"
          },{
            crossOrigin: true,
            headers:{
              'Content-Type':'application/json' 
            }

          }).then(function(res){
            console.log(res.json());
            if(res.json().success == 1){
              this.status.hot_not = msgText;
            }else{
              console.log(res.json().error);
            }
          });
      	},
      	onDetailedInfo: function(index){
          this.status.text = '删除该请求';
           this.status.selected = index;
           var list = this.msgList[index];
           this.$http.post(this.domain+'getParentInfo',{
              "pd_id": list.pd,
              "format": true,
            },{
              crossOrigin: true,
              headers:{
                'Content-Type':'application/json'  
              }
            }).then(function(res){
               if(res.json().success == 0){
                console.log(res.json().error);
               }else{
                this.detailedList = res.json();
                this.status.isTutorInfo = true;
               }
            })
      	},
        onDelete: function(index){          
          this.$http.post(this.domain+'/deleteOrder',{
              'oa_id': this.msgList[index].oa_id,
            }, {
            crossOrigin: true,
            headers:{
              'Content-Type':'application/json' 
            } 
          }).then(function(res) {
            if (res.json().success == 1) {
              var self = this;
              this.status.text = '该请求已删除';
              this.timer && clearTimeout(this.timer);
              this.timer = setTimeout(function(){
                self.msgList.splice(index,1);
                self.status.isTutorInfo = false;
              }, 800);
            }else{
              console.log(res.json().error);
            }
            
          });        
        },
        onClose: function(){
        	this.status.isTutorInfo = false;
        }
      },
	});
})();
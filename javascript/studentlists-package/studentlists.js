var Util = {
    toDict: function(sequence, key_extractor) {
        var key_extractor_fn = null;
        if ((typeof key_extractor) == "string")
            key_extractor_fn = function(el) {return el[key_extractor];};
        else
            key_extractor_fn = key_extractor;

        var dict = {};
        for (var i in sequence) {
            var item = sequence[i];
            dict[key_extractor_fn(item)] = item;
        }
        return dict;
    },
    
    bindEventsToObject: function(source, events, handler) {
        for (var i in events) {
            (function(method) {
                source.bind(events[i], function(event) {
                    handler[method](event);
                });
            })(events[i]);
        }
    },

    parseQueryString: function(url) {
        var qs = {};
        var parts = url.split('?');
        if(parts.length == 2) {
            var querystring = parts[1].split('&');
            for(var i = 0; i<querystring.length; i++) {
                var kv = querystring[i].split('=');
                if(kv[0].length > 0) //fix trailing &
                    qs[kv[0]] = kv[1];
            }
        }
        return qs;
    },

    toQueryString: function(hash, kvjoin, eljoin) {
        kvjoin = kvjoin || '=';
        eljoin = eljoin || '&';
        var qs = [];
        for(var key in hash) {
            if(hash.hasOwnProperty(key))
                qs.push(key + kvjoin + hash[key]);
        }
        return qs.join(eljoin);
    }
};

var StudentLists = {

    //********** data model methods

    isStudentInGroup: function(student_id, group_id) {
        var student = StudentLists.students_by_id[student_id];
        for (var i in student.study_groups) {
            if (student.study_groups[i].key == group_id) {
                return true;
            }
        }
        return false;
    },

    addGroup: function(group) {
        StudentLists.study_groups.push(group);
        StudentLists.study_groups_by_id[group.key] = group;
    },

    removeGroup: function(group_id) {
        jQuery.each(StudentLists.students, function(i, s) {
            StudentLists.removeStudentFromGroup(s, group_id);
        });

        var groups = [];
        for (var i in StudentLists.study_groups) {
            var group = StudentLists.study_groups[i];
            if (group.key != group_id) {
                groups.push(group);
            }
        }
        StudentLists.study_groups = groups;

        StudentLists.generateGroupIndices();
    },

    removeStudent: function(student) {
        var index = StudentLists.students.indexOf(student);
        if (index != -1)
            StudentLists.students.splice(index, 1);

        StudentLists.generateStudentIndices();
    },

    removeStudentFromGroup: function(student, group_id) {
        var groups = [];
        for (var i in student.study_groups) {
            var group = student.study_groups[i];
            if (group.key != group_id) {
                groups.push(group);
            }
        }
        student.study_groups = groups;
    },

    addStudentToGroup: function(student, group_id) {
        student.study_groups.push(StudentLists.study_groups_by_id[group_id]);
    },

    generateGroupIndices: function() {
        StudentLists.study_groups_by_id = Util.toDict(StudentLists.study_groups, 'key');
    },

    generateStudentIndices: function() {
        StudentLists.students_by_id = Util.toDict(StudentLists.students, 'key');
        StudentLists.students_by_email = Util.toDict(StudentLists.students, 'email');
    },


    // *********** UI methods

    dropdownEl: null,
    currentStudent: null,
    currentGroup: null,

    init: function() {
        // indexes
        StudentLists.generateGroupIndices();
        StudentLists.generateStudentIndices();

        addStudentTextBox.init();

        // create lists
        addListTextBox.init();
        $('#newlist-button').click(function(event) {
            event.preventDefault();
            addListTextBox.element.show().focus();
        });
        
        // delete list
        $('#delete-group').click(StudentLists.deleteGroupClick);

        // change visible list
        $('.bullet').click(StudentLists.listClick);

        // lists dropdown menu
        $('.edit-lists').click(StudentLists.openListsMenuClick);
        StudentLists.dropdownEl = $('.edit-lists-options');
        StudentLists.redrawListsMenu();
        StudentLists.dropdownEl.click(function(event) {event.stopPropagation();});
        $('html').click(StudentLists.hideMenu);

        // inline delete student-group
        $('.student-row .delete-button').click(StudentLists.deleteStudentClick);

        // quick removal of students from groups via label
        // $('.removecross').click(StudentLists.groupLabelClick);


        // show initial page
        // todo: remember this with a cookie!
        $('#group-allstudents a').click();
    },

    deleteGroupClick: function(event) {
        event.preventDefault();
        if (StudentLists.currentGroup != 'allstudents' &&
            StudentLists.currentGroup != 'requests') {

            $.ajax({
                type: 'POST',
                url: '/deletegroup',
                data: 'group_id=' + StudentLists.currentGroup,
                success: function(data, status, jqxhr) {
                    $('#custom-groups .group-'+StudentLists.currentGroup).remove();
                    StudentLists.removeGroup(StudentLists.currentGroup);
                    StudentLists.redrawListsMenu();
                    $('#group-allstudents a').click();

                }
            });
        }
    },

    deleteStudentClick: function(event) {
        event.preventDefault();
        var rowEl = $(event.currentTarget).parents('.student-row');
        var student_id = rowEl.attr('id').substring('student-'.length);
        var student = StudentLists.students_by_id[student_id];

        if (StudentLists.currentGroup == 'allstudents') {
            // this deletes the student-coach relationship: be sure
            var sure = confirm('Are you sure you want to stop coaching this student?');
            if (sure) {
                $.ajax({
                    type: 'GET',
                    url: '/unregisterstudent',
                    data: 'student_email='+student.email,
                    success: function(event) {
                        // update data model
                        StudentLists.removeStudent(student);

                        // update view
                        $('#student-'+student.key).remove();
                        StudentLists.redrawListView();
                    }
                });
            }
        }
        else if (StudentLists.currentGroup == 'requests') {
            var email = rowEl.find('.student-name').html();
            $.ajax({
                type: 'GET',
                url: '/acceptcoach',
                data: 'accept=0&student_email='+email,
                success: function(data, status, jqxhr) {
                    // update data model
                    var requests = [];
                    for (var i in StudentLists.coach_requests) {
                        var request = StudentLists.coach_requests[i];
                        if (request != email) {
                            requests.push(request);
                        }
                    }
                    StudentLists.coach_requests = requests;

                    // update UI
                    rowEl.remove();
                    StudentLists.redrawListView();
                }
            });
        }
        else {
            var group_id = StudentLists.currentGroup;
            StudentLists.removeStudentFromGroupAjax(student, group_id);
        }
    },

    listClick: function(event) {
        event.preventDefault();
        var $selectedList = $(event.currentTarget);

        var group_id = Util.parseQueryString($selectedList.attr('href'))['group_id'] || 'allstudents';
        if(group_id == StudentLists.currentGroup) {
            return;
        }
        StudentLists.currentGroup = group_id;

        $('.bullet-active').removeClass('bullet-active');
        $selectedList.addClass('bullet-active');

        StudentLists.redrawListView();
    },

    redrawListView: function() {
        // show or hide students depending on group membership
        var nstudents = 0;
        var title = 'Students';
        var countstring = 'student';

        if(StudentLists.currentGroup == 'requests') {
            $('#actual-students').hide();
            $('#requested-students').show();
            nstudents = $('#requested-students .student-row').length;

            title = 'Requests';
            $('#delete-group').hide();
            countstring = 'potential student';
        }
        else {
            $('#requested-students').hide();
            $('#actual-students').show();

            if(StudentLists.currentGroup=='allstudents') {
                var all = $('#actual-students .student-row');
                all.show();

                nstudents = all.length;
                title = 'All students';
                $('#delete-group').hide();
            }
            else {
                $('#actual-students .student-row').each(function() {
                    var el = $(this);
                    var student_id = el.attr('id').substring('student-'.length);
                    if(StudentLists.isStudentInGroup(student_id, StudentLists.currentGroup)) {
                        el.show();
                        nstudents++;
                    }
                    else {
                        el.hide();
                    }
                });

                var group = StudentLists.study_groups_by_id[StudentLists.currentGroup];
                title = group.name;
                $('#delete-group').show();
            }
        }

        var nstudentsStr = nstudents.toString() + ' '
                                                + countstring
                                                + (nstudents==1 ? '' : 's');
        $('#nstudents').html(nstudentsStr);
        $('.students-header h2').html(title);
    },

    groupLabelClick: function(event) {
        event.stopPropagation();
        event.preventDefault();
        var url = unescape($(event.currentTarget).attr('href'));
        var qs = Util.parseQueryString(url);
        var student = StudentLists.students_by_email[qs['student_email']];
        StudentLists.removeStudentFromGroupAjax(student, qs['group_id']);
    },

    //*********** list dropdown menu methods

    redrawListsMenu: function() {
        var menu = StudentLists.dropdownEl;
        menu.children().remove();

        // add a line for each group
        jQuery.each(StudentLists.study_groups, function() {
            var group = this;
            var el = '<label class="list-option"><input type="checkbox" id="checkbox-' + group.key + '" />' + group.name + '</label>';
            menu.append(el);
        });

        // wire up events
        menu.find('input').click(StudentLists.listOptionClick);
    },

    openListsMenuClick: function(event) {
        event.stopPropagation();
        event.preventDefault();

        var $menuButton = $(this);
        var student_id = $menuButton.parents('.student-row').attr('id')
                               .substring("student-".length);
        var student = StudentLists.students_by_id[student_id];
        if(StudentLists.currentStudent == student) {
            StudentLists.hideMenu();
            return true;
        }
        StudentLists.currentStudent = student;
        $menuButton.addClass('active');

        // get dropdown in position
        StudentLists.dropdownEl.show();

        var offset = $menuButton.offset();
        offset.top += $menuButton.outerHeight() - 1;
        offset.left += ($menuButton.outerWidth() - StudentLists.dropdownEl.outerWidth());
        StudentLists.dropdownEl.offset(offset);

        // check the right boxes
        $('.list-option input').removeAttr('checked');
        for (var i in student.study_groups) {
            var group = student.study_groups[i];
            $('#checkbox-'+group.key).attr('checked', true);
        }
    },

    hideMenu: function() {
        StudentLists.dropdownEl.hide();
        StudentLists.currentStudent = null;
        $('.active.edit-lists').removeClass('active');
    },

    listOptionClick: function(event) {
        var group_id = $(this).attr('id').substring("checkbox-".length);
        if ($(this).attr('checked')) {
            StudentLists.addStudentToGroupAjax(StudentLists.currentStudent, group_id);
            // todo: make group label appear under student
        }
        else {
            StudentLists.removeStudentFromGroupAjax(StudentLists.currentStudent, group_id);
            // todo: remove group label from under student
        }
    },

    addStudentToGroupAjax: function(student, group_id) {
        $.ajax({
            type: 'POST',
            url: '/addstudenttogroup',
            data: 'student_email='+student.email+'&group_id='+group_id,
            success: function() {
                // update data model
                StudentLists.addStudentToGroup(student, group_id);

                // todo: add group label
                // $('#student-'+student.key).find('.group-'+group_id).hide();
            }
        });
    },

    removeStudentFromGroupAjax: function(student, group_id) {
        $.ajax({
            type: 'POST',
            url: '/removestudentfromgroup',
            data: 'student_email='+student.email+'&group_id='+group_id,
            success: function() {
                // update data model
                StudentLists.removeStudentFromGroup(student, group_id);

                // update view

                // hide label
                // $('#student-'+student.key).find('.group-'+group_id).hide();

                // hide row from screen if visible
                if (StudentLists.currentGroup == group_id) {
                    $('#student-'+student.key).hide();
                }
            }
        });
    }
};

var addListTextBox = {
    element: null,
    
    init: function() {
        this.element = $('#newlist-box');
        Util.bindEventsToObject(this.element, ['keypress', 'keyup', 'focusout'], this);
    },
    
    keypress: function(event) {
        if (event.which == '13') { // enter
            event.preventDefault();
            this.createList(event);
        }
    },
    
    keyup: function(event) {
        if (event.which == '27') { // escape
            this.hide();
        }
    },
    
    focusout: function(event) {
        this.hide();
    },

    createList: function(event) {
        var listname = this.element.val();
        
        if (!listname) {
            this.hide();
            return;
        }
        
        this.element.attr('disabled', 'disabled');
        $.ajax({
            type: 'POST',
            url: '/creategroup',
            data: 'group_name=' + listname,
            dataType: 'json',
            success: function(data, status, jqxhr) {
                var group = data;
                StudentLists.addGroup(group);

                // add a new item to the sidebar
                var $el = $('<li class="group-'+group.key+'"><a href="students?group_id='+group.key+'" class="bullet">'+group.name+'</a></li>');
                $('#custom-groups').append($el);
                $el.find('a').click(StudentLists.listClick);

                // add a new item to the dropdown menu
                StudentLists.redrawListsMenu();
            },
            complete: function(){addListTextBox.hide();}
        });
    },

    hide: function() {
        this.element.val('').hide().removeAttr('disabled');
        $('#newlist-button').focus();
    }
};

var addStudentTextBox = {
    element: null,

    init: function() {
        this.element = $('#textbox-container input');
        
        Util.bindEventsToObject(this.element, ['focusin', 'focusout', 'keyup'], this);
    },

    focusin: function(event) {
        this.element.val('');
    },

    focusout: function(event) {
        this.element.val("Type a student's email address to propose becoming their coach");
    },

    keyup: function(event) {
        if (event.which == '13') {
            var email = addStudentTextBox.element.val();
            $.ajax({
                type: 'POST',
                url: '/requeststudent',
                data: 'student_email='+email,
                success: function(data, status, jqxhr) {
                    // data model
                    StudentLists.coach_requests.push(email);

                    // UI
                    addStudentTextBox.element.val('');

                    var el = $('#tmpl .student-row').clone();
                    el.find('.student-name').html(email);
                    el.hide().prependTo('#requested-students');
                    el.find('.delete-button').click(StudentLists.deleteStudentClick);
                    el.fadeIn();

                    $('#group-requests a').click();
                }
            });
        }
        else if (event.which == '27') {
            this.element.blur();
        }
    }
};

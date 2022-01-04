// This script has to be placed in static/js/ folder
// This script is socketio client.
// This is jquery library (subset of js).

// eslint-disable-next-line no-unused-vars
function refreshStatus( stepDetails ) {

  const actionSeq = stepDetails.action_seq;
  const stepSeq = stepDetails.step_seq;

  console.log( "Updating for action " + actionSeq + "-" + stepSeq + "." );

  const stepName = actionSeq + "-" + stepSeq;
  $( "#card-" + actionSeq ).addClass( "bg-primary" ).addClass( "text-white" );
  $( "#card-" + stepName ).addClass( "bg-primary" ).addClass( "text-white" );

  const namespace = "/broadcast-queue";
  // eslint-disable-next-line no-undef
  var socket = io.connect( "http://" + document.domain + ":" + location.port + namespace );
  // This ^ is not a webpage. This ^ is a socketio. Domain: port must be the ip:port of the socketio server.
  socket.on( "new_actual_exec", function( data ) {
    console.log( data );
    var actualExec = data.actual_exec;
    var nextExecIndex = data.step_details['exec_index']
    var nextStepSeq = data.step_details['step_seq'];
    var nextActionSeq = data.step_details['action_seq'];

    var nextStepName = nextActionSeq + "-" + nextStepSeq + "-" + nextExecIndex;
    var nextExecName = "Exec " + (parseInt(nextExecIndex) + 1) + ": " + actualExec //need to +1 for disp
    //    #card-(some variable) is the id that's defined in html
    //    removeClass and addClass is from jquery
    console.log( "Updating actual exec for action " + nextStepName + "." );
    $( "#exec-" + nextStepName ).html(nextExecName);

    socket.emit( "received-message", { "status": "success", "data": data } );
  } );
  // This is the same as the following in py code:
  // @socketio.on('event', namespace='/namespace')
  socket.on( "new_broadcast", function( data ) {
    console.log( data );
    var prevStepSeq = data.prev_step_seq;
    var prevActionSeq = data.prev_action_seq;
    var nextStepSeq = data.next_step_seq;
    var nextActionSeq = data.next_action_seq;

    var prevStepName = prevActionSeq + "-" + prevStepSeq;
    var nextStepName = nextActionSeq + "-" + nextStepSeq;

    console.log( "Deactivating for action " + prevActionSeq + "-" + prevStepName + "." );
    //    #card-(some variable) is the id that's defined in html
    //    removeClass and addClass is from jquery
    $( "#card-" + prevActionSeq ).removeClass( "bg-primary" ).removeClass( "text-white" );
    $( "#card-" + prevStepName ).removeClass( "bg-primary" ).removeClass( "text-white" );

    console.log( "Activating for action " + nextActionSeq + "-" + nextStepName + "." );
    $( "#card-" + nextActionSeq ).addClass( "bg-primary" ).addClass( "text-white" );
    $( "#card-" + nextStepName ).addClass( "bg-primary" ).addClass( "text-white" );

    socket.emit( "received-message", { "status": "success", "data": data } );
  } );

    // For any js script that's updated, you have to crtl+F5 to hard refresh the website


}

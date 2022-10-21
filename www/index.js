var cfg_online = ``;

var cfg_main = {};


cfg_main.version = "0.0.1";
cfg_main.lng = "de"; //Language
cfg_main.lng_auto = true;

cfg_main.url = ""; //URL mode = all prefix/suffix & websocket disabled
cfg_main.url_web_prefix = window.location.protocol + "//";
cfg_main.url_web_suffix = "/index";
cfg_main.url_web_suffix_upload = "/upload";
cfg_main.url_ws_prefix = "ws://";
cfg_main.url_ws_suffix = ":81/ws";
cfg_main.url_icon = "images/";
cfg_main.url_images = "images/";

cfg_main.json = "json";
cfg_main.json_uid = "uid";
cfg_main.json_version = "version";
cfg_main.json_lng = "lng";
cfg_main.json_cmd = "cmd";
cfg_main.json_cmd_mode = "cmd_mode";
cfg_main.json_ping = "ping";
cfg_main.json_session = "session";
cfg_main.json_config = "config";
cfg_main.json_config_live = "config_live";
cfg_main.json_data = "data";
cfg_main.json_data_send = "data";
cfg_main.json_data_live = "data_live";
cfg_main.json_data_live_leds = "data_live_leds";
cfg_main.json_result = "result";
cfg_main.json_msg = "msg";
cfg_main.json_toasts = "toasts";
cfg_main.json_val_session = "session_";
cfg_main.json_val_cfg = "get_config";
cfg_main.json_val_cfg_data = "get_config_data";
cfg_main.json_val_data = "get_data";
cfg_main.json_val_get = "get_data";
cfg_main.json_val_set = "set_data";
cfg_main.json_val_upload = "upload";
cfg_main.json_val_ping = "1";
cfg_main.json_val_live_cfg = "get_live_config";
cfg_main.json_val_live_cfg_data = "get_live_config_data";
cfg_main.json_val_live_data = "get_live_data";

cfg_main.delimiter_1 = ";";
cfg_main.delimiter_2 = ",";
cfg_main.delimiter_val = "=";

cfg_main.get_timeout = 60; //Seconds
cfg_main.get_size_url = 4094; //Characters
cfg_main.get_size_header = 4094; //Characters
cfg_main.get_all = false;
cfg_main.post_timeout = 20; //Seconds
cfg_main.post_upload_timeout = 30; //Seconds
cfg_main.reconnect_delay = 5; //Seconds
cfg_main.reconnect_timeout = 60; //Seconds
cfg_main.reload_delay = 10; //Seconds
cfg_main.ping = true;
cfg_main.ping_delay = 10; //Seconds
cfg_main.ping_timeout = 30; //Seconds
cfg_main.ping_timeout = 30; //Seconds
cfg_main.toast_timeout = 3; //Seconds
cfg_main.toasts_timeout = 5; //Seconds

cfg_main.con_type = false; //true=websocket with http fallback, false=http
cfg_main.mode_load = false; //true=config+data togehter, false=config+data separated
cfg_main.mode_test = false; //true=operation without connection (Test-Mode), false=normal operation
cfg_main.mode_screen = false;
cfg_main.slide_tab = true;
cfg_main.slide_tab_area_ratio = 0.12;
cfg_main.slide_menu = true;
cfg_main.slide_menu_up = true;
cfg_main.slide_menu_area_ratio = 0.12;
cfg_main.slide_menu_area_size = 40;
cfg_main.scroll_page = true;
cfg_main.scroll_tab = true;
cfg_main.save_view = true;
cfg_main.save_data = true;
cfg_main.submit_empty = false;
cfg_main.submit_global = true;

cfg_main.window = "Config Interface";
cfg_main.header = "Config Interface";
cfg_main.class = "";
cfg_main.class_menu = "m-resp";
cfg_main.class_container = "";
cfg_main.style = "";
cfg_main.icon = "";

cfg_main.msg_btn = false;
cfg_main.msg_btn_error = true;
cfg_main.msg_btn_confirm = true;
cfg_main.msg_file_mode = ["Bitte die IP Adresse des Gerätes angeben!", "Datei Modus"];
cfg_main.msg_error = [" ", "Fehler"];
cfg_main.msg_error_val = ["Datenübertragung fehlerhaft!", "Fehler"];
cfg_main.msg_error_con = ["Verbindung fehlgeschlagen!", "Fehler"];
cfg_main.msg_error_empty = ["Keine Daten zum senden!", "Fehler"];
cfg_main.msg_error_upload = ["Upload fehlgeschlagen!", "Fehler"];
cfg_main.msg_con = ["Verbinde, bitte warten...", "Info"];
cfg_main.msg_con_error = ["Verbindung fehlgeschlagen! Neu verbinden in Sekunden:", "Fehler"];
cfg_main.msg_con_timeout = ["Verbindung fehlgeschlagen! Maximale Anzahl an Versuchen erreicht!", "Fehler"];
cfg_main.msg_reconnect = ["Neustart, bitte warten...", "Info"];
cfg_main.msg_cfg_load = ["Lade Konfiguration, bitte warten...", "Info"];
cfg_main.msg_data_load = ["Lade Daten, bitte warten...", "Info"];
cfg_main.msg_cfg_data_load = ["Lade Konfiguration + Daten, bitte warten...", "Info"];


var cfg_local;
var cfg;
var data;

var uids;

var send_val_timer;

var content_header;

var input_colorpicker;
var input_colorpicker_field;

var input_range;

var ws;
var ws_power = true;


//start
$(document).ready(function() {
  setup();
});


//setup
function setup(mode = "") {
  live_check(false);

  if (cfg_main.lng_auto) cfg_main.lng = navigator.language || navigator.userLanguage || cfg_main.lng;
  cfg_main.lng = cfg_main.lng.split("-")[0];
  cfg_main.lng.toLowerCase();

  uids = [];
  send_val_timer = {};

  reset_content();

  cfg = {};
  cfg.main = cfg_main;

  cfg_apply();

  if (cfg.main.mode_test) {
    cfg_process(jQuery.parseJSON(cfg_online));
  } else {
    show(false);

    data = {};
    data.data_send = {};
    data.con_cfg = false;
    data.con_data = false;
    data.con_live = false;
    if (!cfg.main.con_type) data.con_live = true;
    data.reconnect_delay = 0;
    data.reconnect_delay_ws = 0;
    data.reconnect_timeout = 0;
    data.reconnect_timeout_ws = 0;

    cfg_local_load();

    if (cfg_local.data.lng) {
      if (cfg_local.data.lng.length == 2) {
        cfg_main.lng = cfg_local.data.lng;
        cfg.main.lng = cfg_local.data.lng;
      }
    }

    if (cfg.main.url == "") {
      if (window.location.protocol == "file:") {
        if (!cfg_local.address) cfg_local.address = prompt(cfg.main.msg_file_mode[1]);
      }
      if (!cfg_local.address) cfg_local.address = window.location.host;
      if (cfg.main.url_web_suffix.startsWith(":")) {
        cfg_local.url_web = cfg.main.url_web_prefix + cfg_local.address.replace(/:.*/, "") + cfg.main.url_web_suffix;
      } else {
        cfg_local.url_web = cfg.main.url_web_prefix + cfg_local.address + cfg.main.url_web_suffix;
      }
      if (cfg.main.url_ws_suffix.startsWith(":")) {
        cfg_local.url_ws = cfg.main.url_ws_prefix + cfg_local.address.replace(/:.*/, "") + cfg.main.url_ws_suffix;
      } else {
        cfg_local.url_ws = cfg.main.url_ws_prefix + cfg_local.address + cfg.main.url_ws_suffix;
      }
    } else {
      cfg_local.url_web = cfg.main.url;
      cfg_local.url_ws = cfg.main.url;
      cfg.main.con_type = false;
      data.con_live = true;
    }

    cfg_local_save();

    if ("WebSocket" in window && cfg.main.con_type) {
      cfg_local.con_type = true;

      ws_setup();
    } else {
      cfg_local.con_type = false;
    }

    if (cfg.main.mode_load) {
      cfg_data_load(true, true, mode);
    } else {
      cfg_data_load(true, false, mode);
    }
  }
}


//websocket
function ws_setup() {
  if (!cfg_local.con_type) return;
  ws_power = true;

  show(false);
  state_show(false);
  spinner_show();
  toast_show(cfg.main.msg_con, false, 0);

  /*if (ws != undefined)
  {
    ws.close();
    event.preventDefault();
    event.returnValue = "";
  }*/

  ws = new WebSocket(cfg_local.url_ws);

  ws.onopen = function () {
    data.con_live = true;
    show_update();
    state_show();
    data.reconnect_delay_ws = 0;
    data.reconnect_timeout_ws = 0;

    if (!data.con_cfg) {
      cfg_data_load(true, false);
    } else if (!data.con_data) {
      cfg_data_load(false, true);
    } 

    if (cfg.main.ping) {
      data.ping = Date.now();
      setTimeout(function() { ws_ping(); }, cfg.main.ping_delay*1000);
    }
  };

  ws.onmessage = function (evt) {
    var d = JSON.parse(evt.data);
    if (d[cfg.main.json_ping]) data.ping = Date.now();
    if (d[cfg.main.json_data_live_leds]) update_val_live_leds(d[cfg.main.json_data_live_leds]);
    update(d);
    if (error_check(d)) {
      if (d[cfg.main.json_data] && !data.con_data) {
        data.con_data = true;
        show_update();
        if (!d[cfg.main.json_data] && !data.con_data) cfg_data_load(false, true);
      }
    }
  };

  ws.onclose = function (evt) {
    ws.close();
    if (ws_power) {
      data.con_data = false;
      show(false);
      state_show(false);
      spinner_show(false);
      data.reconnect_delay_ws += cfg.main.reconnect_delay;
      data.reconnect_timeout_ws += data.reconnect_delay_ws
      if (data.reconnect_timeout_ws >= cfg.main.reconnect_timeout) {
        toast_show(cfg.main.msg_con_timeout, true, 0);
      } else {
        cfg.main.msg_con_error = val_to_array(cfg.main.msg_con_error, false);
        toast_show([cfg.main.msg_con_error[0] + ' ' + data.reconnect_delay_ws, cfg.main.msg_con_error[1]], true, 0);
        setTimeout(function() { ws_setup(); }, data.reconnect_delay_ws*1000);
      }
    }
  };

  ws.onerror = function (error) {
    if (ws_power) {
    }
  }
}


function ws_close() {
  if (!cfg_local.con_type) return;
  ws.close();
  event.preventDefault();
  event.returnValue = "";
}


function ws_ping() {
  if (!cfg_local.con_type) return;
  
  if (Date.now() - data.ping >= cfg.main.ping_timeout*1000) {
    ws.close();
    event.preventDefault();
    event.returnValue = "";

    ws_setup();
  } else {
    json = {};
    json[cfg.main.json_uid] = uid();
    json[cfg.main.json_version] = cfg.main.version;
    json[cfg.main.json_lng] = cfg.main.lng;
    json[cfg.main.json_ping] = cfg.main.json_val_ping;
    ws.send(JSON.stringify(json));
    setTimeout(function() { ws_ping(); }, cfg.main.ping_delay*1000);
  }
}


//cfg_local
function cfg_local_load() {
  if (localStorage.getItem("cfg_local")) {
    cfg_local = jQuery.parseJSON(localStorage.getItem("cfg_local"));
  } else {
    cfg_local = {};
  }

  if (!cfg_local["data"]) cfg_local["data"] = {};
}


function cfg_local_save() {
  localStorage.setItem("cfg_local", JSON.stringify(cfg_local));
}


function cfg_local_process() {
  if (cfg.main.save_view) {
    if (cfg_local["page"]) page_show_set(cfg_local["page"]);

    if (cfg_local["tab"]) {
      $.each(cfg.c, function(page_i, page) {
        if (page.t == "page" && cfg_local["tab"][page_i]) {
          tab_show_set(cfg_local["tab"][page_i], $("[data-page=" + page_i + "]"));
        }
      });
    }

    if (cfg_local["group"]) {
      $.each(cfg_local["group"], function(group, index) {
        $("[data-group=" + group + "]").each(function() {
          if ($(this).attr("data-group-index") == index) {
            $(this).find(".body").removeClass("hide");
          } else {
            $(this).find(".body").addClass("hide");
          }
        });
      });
    }
  }

  if (cfg.main.save_data) {
    if (cfg_local["data"]) {
      $.each(cfg_local["data"], function(key, val) {
        update_val(key, val, "local");
      });
    }
  }
}


//cfg+data
function cfg_data_load(mode_cfg = false, mode_data = false, mode = "") {
  show(false);
  spinner_show();

  var uid_current = uid();
  json = {};
  json[cfg.main.json_uid] = uid_current;
  json[cfg.main.json_version] = cfg.main.version;
  json[cfg.main.json_lng] = cfg.main.lng;
  if (mode != "") json[cfg.main.json_cmd_mode] = mode;

  if (mode_cfg && mode_data) {
    toast_show(cfg.main.msg_cfg_data_load, false, 0);
    json[cfg.main.json_cmd] = cfg.main.json_val_cfg_data;
  } else if (mode_cfg) {
    toast_show(cfg.main.msg_cfg_load, false, 0);
    json[cfg.main.json_cmd] = cfg.main.json_val_cfg;
  } else if (mode_data) {
    toast_show(cfg.main.msg_data_load, false, 0);
    json[cfg.main.json_cmd] = cfg.main.json_val_data;
    if (!cfg.main.get_all) {
      var data_array = [];
      $.each(cfg.data_fields, function(i, el){ if ($.inArray(el, data_array) === -1) data_array.push(el); });
      json[cfg.main.json_data] = data_array;
    }
  }

  if (cfg_local.con_type) {
    ws.send(JSON.stringify(json));
  } else {
    var ajax_headers = {};
    var ajax_data = ""
    var json_str = JSON.stringify(json);
    if (cfg_local.url_web.length + json_str.length >= cfg.main.get_size_url) {
      if (json_str.length <= cfg.main.get_size_header) ajax_headers[cfg.main.json] = json_str;
    } else {
      ajax_data = cfg.main.json + '=' + json_str;
    }
    $.ajax({
      type: 'GET',
      url: cfg_local.url_web,
      timeout: cfg.main.get_timeout*1000,
      headers: ajax_headers,
      data: ajax_data,
      dataType: 'json',
      cache: false,
      success: function(d) {
        data.reconnect_delay = 0;
        data.reconnect_timeout = 0;
        update(d);
        if (error_check(d)) {
          if (d[cfg.main.json_data] && !data.con_data) {
            data.con_data = true;
            show_update();
          }
          if (!d[cfg.main.json_data] && !data.con_data) cfg_data_load(false, true);
        }
      }, error: function(d) {
        spinner_show(false);
        data.reconnect_delay += cfg.main.reconnect_delay;
        data.reconnect_timeout += data.reconnect_delay
        if (data.reconnect_timeout >= cfg.main.reconnect_timeout) {
          toast_show(cfg.main.msg_con_timeout, true, 0);
        } else {
        cfg.main.msg_con_error = val_to_array(cfg.main.msg_con_error, false);
        toast_show([cfg.main.msg_con_error[0] + ' ' + data.reconnect_delay, cfg.main.msg_con_error[1]], true, 0);
        setTimeout(function() { cfg_data_load(mode_cfg, mode_data); }, data.reconnect_delay*1000);
        }
      }
    });
  }
}


//error
function error_check(d) {
  if (d[cfg.main.json_result]) {
    if (d[cfg.main.json_result] != 1) {
      spinner_show(false);
      if (d[cfg.main.json_msg]) {
        toast_show([d[cfg.main.json_msg], cfg.main.msg_error[1]], true, 0);
      } else {
        toast_show(cfg.main.msg_error, true, 0);
      }
      return false;
    }
  } else {
    spinner_show(false);
    toast_show(cfg.main.msg_error_val, true, 0);
    return false;
  }
  return true;
}


//cfg
function cfg_process(d) {
  reset_content();

  cfg = {};
  cfg.main = cfg_main;
  $.extend(true, cfg, d);

  if(!cfg.vd) cfg.vd = [];
  if(!cfg.id) cfg.id = [];
  if(!cfg.msgsd) cfg.msgsd = [];
  if(!cfg.r_cad) cfg.r_cad = [];
  if(!cfg.pa_cad) cfg.pa_cad = [];

  cfg_apply();

  cfg.data_fields = [];

  if (cfg.c_main) {
    var tmp = $("#tmp_content").clone();
    tmp.removeAttr("id");
    add_content(cfg.c_main, tmp);
    $("#container").append(tmp);
  }

  if (cfg.c_header_fix) {
    var tmp = $("#tmp_content_header_fix").clone();
    tmp.removeAttr("id");
    add_content(cfg.c_header_fix, tmp);
    $("#container").append(tmp);
  }

  if (cfg.c_header) {
    var tmp = $("#tmp_content_header").clone();
    tmp.removeAttr("id");
    add_content(cfg.c_header, tmp);
    $("#container").append(tmp);
  }

  add_content_page(cfg.c, $("#container"));

  if (cfg.c_footer) {
    var tmp = $("#tmp_content_footer").clone();
    tmp.removeAttr("id");
    add_content(cfg.c_footer, tmp);
    $("#container").append(tmp);
  }
  
  if (cfg.c_footer_fix) {
    var tmp = $("#tmp_content_footer_fix").clone();
    tmp.removeAttr("id");
    add_content(cfg.c_footer_fix, tmp);
    $("#container").append(tmp);
  }

  cfg_addons_process();

  cfg_active_process();

  cfg_local_process();

  data.con_cfg = true;
  show_update();

  var page = $(".active[data-type=page]");
  var tab = page.find(".active[data-type=tab]");
  tab.find("[autofocus=autofocus]").first().focus();
}


function cfg_apply() {
  if (cfg.main.w) cfg.main.window = cfg.main.w;
  if (cfg.main.h) cfg.main.header = cfg.main.h;
  if (cfg.main.cl) cfg.main.class = cfg.main.cl;
  if (cfg.main.s) cfg.main.style = cfg.main.s;
  if (cfg.main.i) cfg.main.icon = cfg.main.i;

  if (cfg.main.window) document.title = cfg.main.window;
  if (cfg.main.header) $("#header").html(cfg.main.header);
  if (cfg.main.class) $("#body").addClass(cfg.main.class);
  if (cfg.main.style) $("#body").attr("style", cfg.main.style);
  if (cfg.main.class_menu) $("#container_menu").addClass(cfg.main.class_menu);
  if (cfg.main.class_container) $("#container").addClass(cfg.main.class_container);
  if (cfg.main.icon) $("#header").prepend(add_icon_inline(cfg.main.icon));

  cfg.main.get_timeout = parseInt(cfg.main.get_timeout);
  cfg.main.get_size_url = parseInt(cfg.main.get_size_url);
  cfg.main.get_size_header = parseInt(cfg.main.get_size_header);
  cfg.main.get_all = val_to_bool(cfg.main.get_all);
  cfg.main.post_timeout = parseInt(cfg.main.post_timeout);
  cfg.main.post_upload_timeout = parseInt(cfg.main.post_upload_timeout);
  cfg.main.reconnect_delay = parseInt(cfg.main.reconnect_delay);
  cfg.main.reconnect_timeout = parseInt(cfg.main.reconnect_timeout);
  cfg.main.reload_delay = parseInt(cfg.main.reload_delay);
  cfg.main.ping = val_to_bool(cfg.main.ping);
  cfg.main.ping_delay = parseInt(cfg.main.ping_delay);
  cfg.main.ping_timeout = parseInt(cfg.main.ping_timeout);
  cfg.main.toast_timeout = parseInt(cfg.main.toast_timeout);
  cfg.main.toasts_timeout = parseInt(cfg.main.toasts_timeout);

  cfg.main.con_type = val_to_bool(cfg.main.con_type);
  cfg.main.mode_test = val_to_bool(cfg.main.mode_test);
  cfg.main.mode_screen = val_to_bool(cfg.main.mode_screen);
  cfg.main.slide_tab = val_to_bool(cfg.main.slide_tab);
  cfg.main.slide_tab_area_ratio = parseFloat(cfg.main.slide_tab_area_ratio);
  cfg.main.slide_menu = val_to_bool(cfg.main.slide_menu);
  cfg.main.slide_menu_up = val_to_bool(cfg.main.slide_menu_up);
  cfg.main.slide_menu_area_ratio = parseFloat(cfg.main.slide_menu_area_ratio);
  cfg.main.slide_menu_area_size = parseInt(cfg.main.slide_menu_area_size);
  cfg.main.scroll_page = val_to_bool(cfg.main.scroll_page);
  cfg.main.scroll_tab = val_to_bool(cfg.main.scroll_tab);
  cfg.main.save_view = val_to_bool(cfg.main.save_view);
  cfg.main.save_data = val_to_bool(cfg.main.save_data);
  cfg.main.submit_empty = val_to_bool(cfg.main.submit_empty);
  cfg.main.submit_global = val_to_bool(cfg.main.submit_global);

  cfg_main.msg_btn = val_to_bool(cfg_main.msg_btn);
  cfg_main.msg_btn_error = val_to_bool(cfg_main.msg_btn_error);
  cfg_main.msg_btn_confirm = val_to_bool(cfg_main.msg_btn_confirm);
  cfg.main.msg_file_mode = val_to_array(cfg.main.msg_file_mode, false);
  cfg.main.msg_error = val_to_array(cfg.main.msg_error, false);
  cfg.main.msg_error_val = val_to_array(cfg.main.msg_error_val, false);
  cfg.main.msg_error_con = val_to_array(cfg.main.msg_error_con, false);
  cfg.main.msg_error_empty = val_to_array(cfg.main.msg_error_empty, false);
  cfg.main.msg_error_upload = val_to_array(cfg.main.msg_error_upload, false);
  cfg.main.msg_con = val_to_array(cfg.main.msg_con, false);
  cfg.main.msg_con_error = val_to_array(cfg.main.msg_con_error, false);
  cfg.main.msg_con_timeout = val_to_array(cfg.main.msg_con_timeout, false);
  cfg.main.msg_reconnect = val_to_array(cfg.main.msg_reconnect, false);
  cfg.main.msg_cfg_load = val_to_array(cfg.main.msg_cfg_load, false);
  cfg.main.msg_data_load = val_to_array(cfg.main.msg_data_load, false);
  cfg.main.msg_cfg_data_load = val_to_array(cfg.main.msg_cfg_data_load, false);
  
}


function cfg_addons_process() {
  //colorpicker
  if (input_colorpicker_field) {
    input_colorpicker = new iro.ColorPicker(".colorpicker", {
      width: 260,
      wheelLightness: false,
      wheelAngle: 90,
      id: "colorpicker-" + input_colorpicker_field.n,
      layout: [{component:iro.ui.Wheel,options:{}},{component:iro.ui.Slider,options:{sliderType:'kelvin'}}]
    });

    input_colorpicker.on("input:end", function() {
      send_val(input_colorpicker_field, input_colorpicker.color.hexString.substring(1,7));
    });
  }

  //editor
  tinymce.init( {selector : 'textarea.editor', language :'de', plugins: [
    'advlist autolink autosave link image lists charmap print preview hr anchor pagebreak',
    'searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking',
    'table contextmenu directionality emoticons template textcolor paste fullpage textcolor colorpicker textpattern'],
    toolbar1: 'print | undo redo | cut copy paste | searchreplace | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | fontselect fontsizeselect | forecolor backcolor',
    toolbar2: 'removeformat | bullist numlist | outdent indent blockquote | table | link unlink anchor | subscript superscript | hr charmap insertdatetime | ltr rtl | visualchars visualblocks nonbreaking pagebreak',
    menubar: false,
    paste_as_text: true,
    force_br_newlines : true,
    force_p_newlines : false,
    forced_root_block : '',
    toolbar_items_size: 'small',
    entity_encoding: 'raw',
    setup : function(ed) { ed.on('init', function() { this.getDoc().body.style.fontName = 'Verdana'; this.getDoc().body.style.fontSize = '13px'; }); }
});

  //editor_code
  $('.editor_code').each(function(index, elem){
    CodeMirror.fromTextArea(elem, {
      mode: {
      name: 'php',
      startOpen: true
      },
      lineNumbers: true,
      lineWrapping: true,
      height: 'auto',
      viewportMargin: Infinity
    });
  });

  //range
  input_range = RangeTouch.setup('input[type="range"]', {});
}


function cfg_active_process() {
  var page_a = false;
  $.each(cfg.c, function(page_i, page) {
    if (page.t == "page") {
      if (page.a && !page_a) {
        page_show_set(page_i);
        page_a = true;
      }
      var tab_a = false;
      $.each(page.c, function(tab_i, tab) {
        if (tab.a && !tab_a) {
          tab_show_set(tab_i, $("[data-page=" + page_i + "]"));
          tab_a = true;
        }
      });
    }
  });
}


//data
function data_process(d) {
  $.each(d, function(key, val) {
    update_val(key, val);
  });
}


//session
function session_process(d) {
  $.each(d, function(key, val) {
    update_val(cfg.main.json_val_session + key, val);
  });
}


//reset
function reset_content() {
  if (!content_header) {
    content_header = $("#tmp_header").clone();
    content_header.removeAttr("id");
    $("#tmp_header").html("");
  }

  $("#container_header").html(content_header.html());
  $("#toasts").html("");
  $("#popup_overlay").removeClass("active");
  $("#popup").html("");
  $("#container").html("");
}


//add
function add_content_page(fields, target) {
  var active = false;
  $.each(fields, function(page_i, page) {
    add_menu(page_i, page);

    if (page.t == "page") {
      if (!page.w) page.w = document.title;
      if (!page.h) page.h = $("#header").html();

      var tmp_page = $("#tmp_page").clone();
      tmp_page.removeAttr("id");
      tmp_page.attr("data-type", "page");
      tmp_page.attr("data-page", page_i);
      if (page.l) tmp_page.attr("data-page_name", page.l);
      if (page.get) tmp_page.attr("data-get", page.get);
      if (page.set) tmp_page.attr("data-set", page.set);
      if (page.cmd) tmp_page.attr("data-cmd", page.cmd);
      if (page.cl) tmp_page.addClass(page.cl);

      if (!active) {
        active = true;
        $("[data-pages=" + page_i + "]").addClass("active");
        tmp_page.addClass("active");
        if (page.w) document.title = page.w;
        if (page.h) $("#header").html(page.h);
      }

      var page_submit = "";
      $.each(page.c_header, function(i, field) {
        if (field.t == "submit" || field.t == "submit_confirm") page_submit = page_i;
      });
      $.each(page.c_header_fix, function(i, field) {
        if (field.t == "submit" || field.t == "submit_confirm") page_submit = page_i;
      });
      $.each(page.c_footer, function(i, field) {
        if (field.t == "submit" || field.t == "submit_confirm") page_submit = page_i;
      });
      $.each(page.c_footer_fix, function(i, field) {
        if (field.t == "submit" || field.t == "submit_confirm") page_submit = page_i;
      });

      if (page.c_header_fix) {
        var tmp = $("#tmp_content_header_fix").clone();
        tmp.removeAttr("id");
        add_content(page.c_header_fix, tmp, page_submit);
        tmp_page.append(tmp);
      }

      if (page.c_header) {
        var tmp = $("#tmp_content_header").clone();
        tmp.removeAttr("id");
        add_content(page.c_header, tmp, page_submit);
        tmp_page.append(tmp);
      }

      add_content_tab(page.c, tmp_page, page_submit, page_i);

      if (page.c_footer) {
        var tmp = $("#tmp_content_footer").clone();
        tmp.removeAttr("id");
        add_content(page.c_footer, tmp, page_submit);
        tmp_page.append(tmp);
      }
      
      if (page.c_footer_fix) {
        var tmp = $("#tmp_content_footer_fix").clone();
        tmp.removeAttr("id");
        add_content(page.c_footer_fix, tmp, page_submit);
        tmp_page.append(tmp);
      }

      target.append(tmp_page);
    } else if (page.t == "popup") {
      if (!page.c && page.c_footer) {
        page.c = page.c_footer;
        var tmp = $("#tmp_popup").clone();
        tmp.removeAttr("id");
        tmp.attr("data-type", "popup");
        tmp.attr("data-popup", page_i);
        tmp.attr("data-popup_name", page.l);
        var header = tmp.find(".header");
        header.prepend(page.l);
        header.find(".btn-close").click(function() { popup_close(); });
        if (page.i) header.prepend(add_icon_inline(page.i));
        var body = tmp.find(".body");
        add_content_popup(page.c, body, false, page_i);
        $("#popup").append(tmp);
      }
    }
  });
}


function add_content_tab(fields, target, submit, page_i) {
  var target_tabs = target.find(".tabs");
  var tab_count = 0;
  $.each(fields, function(tab_i, tab) {
    tab_count++;

    var tab_submit = submit;
    var tab_submit_process = true;
    $.each(tab.c, function(i, field) {
      if (field.t == "wizard" || field.t == "wizard_start" || field.t == "card" || field.t == "card_start" || field.t == "cardgroup" || field.t == "cardgroup_start" ||field.t == "fieldset" || field.t == "fieldset_start" ||field.t == "fieldsetgroup" || field.t == "fieldsetgroup_start" || field.t == "group" || field.t == "group_start" || field.t == "tabgroup" || field.t == "tabgroup_start") tab_submit_process = false;
      if (field.t == "wizard_end" || field.t == "card_end" || field.t == "cardgroup_end" || field.t == "fieldset_end" || field.t == "fieldsetgroup_end" || field.t == "group_end" || field.t == "tabgroup_end" || field.t == "end") tab_submit_process = true;
      if ((field.t == "submit" || field.t == "submit_confirm") && tab_submit_process) tab_submit = page_i + "-" + tab_i;
    });

    var tmp_tab = $("#tmp_tab").clone();
    tmp_tab.removeAttr("id");
    tmp_tab.attr("data-type", "tab");
    tmp_tab.attr("data-tab", tab_i);
    if (tab.l) tmp_tab.attr("data-tab_name", tab.l);
    if (tab.get) tmp_tab.attr("data-get", tab.get);
    if (tab.set) tmp_tab.attr("data-set", tab.set);
    if (tab.cmd) tmp_tab.attr("data-cmd", tab.cmd);
    if (tab.cl) tmp_tab.addClass(tab.cl);
    if (tab_i == 0) tmp_tab.addClass("active");

    var tmp_menu = $("#tmp_menu_tab").clone();
    tmp_menu.removeAttr("id");
    tmp_menu.attr("data-type", "tabs");
    tmp_menu.attr("data-tabs", tab_i);
    if (tab_i == 0) tmp_menu.addClass("active");

    var menu_link = tmp_menu.find("a");
    menu_link.html(tab.l);
    menu_link.click(function(){ tab_show(tab_i); return false; });

    if (tab.i) menu_link.prepend(add_icon_inline(tab.i));

    target_tabs.append(tmp_menu);
    add_content(tab.c, tmp_tab, tab_submit);
    target.append(tmp_tab);
  });
  if (tab_count <= 1) target.find(".m-bottom").attr("class", "hide");
}


function add_content_popup(fields, target, submit, page_i) {
  var popup_submit = submit;
  $.each(fields, function(i, field) {
    if (field.t == "submit" || field.t == "submit_confirm") popup_submit = page_i;
  });

  add_content(fields, target, popup_submit);
}


function add_content(fields, target, submit) {
  var target_current = $(document.createDocumentFragment());
  var target_main;
  var target_sub;
  var target_field;

  var target_group;
  var target_group_index;

  var group;
  var group_index;
  var group_type;

  var tmp;
  var tmp_content;

  var submit_current = submit;

  $.each(fields, function(i, field) {
    field.submit = submit_current;

    if (field.t == "group" || field.t == "group_start" || field.t == "slide" || field.t == "slide_start" || field.t == "wizard" || field.t == "wizard_start" || field.t == "tabgroup" || field.t == "tabgroup_start") {
      if ((field.t == "group_start" || field.t == "slide_start" || field.t == "wizard_start" || field.t == "tabgroup_start") && target_main) {
        target_main.find(".bodys").append(target_sub);
        add(target_field, target_main, target_field.t + "_container");
        target.append(target_main);
        target_main = false;
        submit_current = submit;
        target_current = $(document.createDocumentFragment());
      }

      field.t = field.t.split('_')[0];
      if (!target_main) {
        if (field.n) {
          target_group = field.n;
        } else {
          target_group = uid();
        }
        target_group_index = 0;
        if (field.t == "wizard" || field.t == "wizard_start") {
          submit_current = uid();
          field.submit = submit_current;
        }
        target_field = field;
        target.append(target_current);
        if (field.st) {
          target_main = $("#tmp_" + field.t + "_container_changeable").clone();
        } else {
          target_main = $("#tmp_" + field.t + "_container").clone();
        }
      } else {
        target_group_index++;
        target_main.find(".bodys").append(target_sub);
      }
      field.group = target_group;
      field.group_index = target_group_index;
      target_sub = $("#tmp_" + field.t).clone();
      add(field, target_sub);
      if (field.t == "tabgroup" || field.t == "tabgroup_start") {
        add(field, target_main.find(".nav"), "tabgroup_nav");
        target_current = target_sub;
      } else {
        target_current = target_sub.find(".body");
      }

    } else if (field.t == "group_end" || field.t == "slide_end" || field.t == "tabgroup_end" || field.t == "wizard_end") {
      if (target_main) {
        target_main.find(".bodys").append(target_sub);
        add(target_field, target_main, target_field.t + "_container");
        target.append(target_main);
        target_main = false;
        submit_current = submit;
        target_current = $(document.createDocumentFragment());
      }

    } else if (field.t == "card" || field.t == "card_start" || field.t == "cardgroup" || field.t == "cardgroup_start" ||field.t == "fieldset" || field.t == "fieldset_start" ||field.t == "fieldsetgroup" || field.t == "fieldsetgroup_start") {
       if (field.t == "card_start" || field.t == "cardgroup_start" || field.t == "fieldset_start" || field.t == "fieldsetgroup_start") {
         if (!target_main) submit_current = submit;
         if (group) group = false;
         if (tmp) {
           target_current.append(tmp);
           tmp = false;
         }
      }

      if (!target_main) {
        if (add_content_submit(i, fields)) {
          submit_current = uid();
        } else {
          submit_current = submit;
        }
      }
      field.t = field.t.split('_')[0];
      if ((!group || group_type != field.t) && (field.t == "cardgroup" || field.t == "fieldsetgroup")) {
        if (field.n) {
          group = field.n;
        } else {
          group = uid();
        }
        group_index = 0;
        group_type = field.t;
      }
      if (group) {
        field.group = group;
        field.group_index = group_index;
        group_index++;
      }
      if (tmp) {
        if (tmp.find(".body").html() == "") tmp.find(".body").addClass("hide");
        target_current.append(tmp);
      }
      if (field.st && field.t != "cardgroup" && field.t != "fieldsetgroup") {
        tmp = $("#tmp_" + field.t + "_changeable").clone();
      } else {
        tmp = $("#tmp_" + field.t).clone();
      }
      tmp_content = tmp.find(".body");
      add(field, tmp);
    } else if (field.t == "card_end" || field.t == "cardgroup_end" || field.t == "fieldset_end" || field.t == "fieldsetgroup_end" || field.t == "end") {
      if (!target_main) submit_current = submit;
      if (group) group = false;
      if (tmp) {
        target_current.append(tmp);
        tmp = false;
      }

    } else {
      if (tmp) {
        add(field, tmp_content);
      } else {
        add(field, target_current);
      }
    }
  });

  if (tmp) target_current.append(tmp);

  if (target_main) {
    target_main.find(".bodys").append(target_sub);
    add(target_field, target_main, target_field.t + "_container");
    target.append(target_main);
  } else {
    target.append(target_current);
  }
}


function add_content_submit(index, fields) {
  ret = false;
  index_current = 0;
  $.each(fields, function(i, field) {
    if (index_current++ > index) {
      if (field.t == "submit" || field.t == "submit_confirm") {
        ret = true;
        return false;
      }
      if (field.t == "card" || field.t == "card_start" || field.t == "cardgroup" || field.t == "cardgroup_start" ||field.t == "fieldset" || field.t == "fieldset_start" ||field.t == "fieldsetgroup" || field.t == "fieldsetgroup_start" || field.t == "card_end" || field.t == "cardgroup_end" || field.t == "fieldset_end" || field.t == "fieldsetgroup_end" || field.t == "end") {
        ret = false;
        return false;
      }
    }
  });
  return ret;
}


function add_menu(i, field) {
  if (field.m == "fix") {
    var tmp_menu = $("#tmp_menu_fix").clone();
    var menu_link = tmp_menu;
  } else {
    var tmp_menu = $("#tmp_menu").clone();
    var menu_link = tmp_menu.find("a");
  }

  tmp_menu.removeAttr("id");
  if (field.cl) tmp_menu.addClass(field.cl);
  if (field.cl_0) tmp_menu.attr("data-class-0", field.cl_0);
  if (field.cl_1) tmp_menu.attr("data-class-1", field.cl_1);
  if (field.s) tmp_menu.attr("style", field.s);
  if (field.s_0) tmp_menu.attr("data-style-0", field.s_0);
  if (field.s_1) tmp_menu.attr("data-style-1", field.s_1);

  menu_link.html(field.l);

  if (field.i) menu_link.prepend(add_icon_inline(field.i));

  if (field.t == "caption") {
    tmp_menu.removeClass("m-item");
    tmp_menu.addClass("m-caption");
  } else if (field.t == "section") {
    tmp_menu.removeClass("m-item");
    tmp_menu.addClass("m-section");
    menu_link.html("");
  } else if (field.t == "toggle") {
    attr_vs(field);
    if (field.n) cfg.data_fields.push(field.n);
    tmp_menu.attr("data-name", field.n);
    tmp_menu.attr("data-type", field.t);
    if (field.vt) tmp_menu.attr("data-value-type", field.vt);
    if (field.v) {
      field.v = val_to_bool(field.v);
    } else {
      field.v = 0;
    }
    menu_link.attr("data-value", field.v);
    menu_link.click(function(){ set_toggle_val(field, $(this).attr("data-value")); menu_close(); return false; });
  } else if (field.t == "button") {
    if (!field.n) return
    if (!field.v) field.v = "";
    menu_link.click(function(){ send_val(field, field.v); menu_close(); return false; });
  } else if (field.t == "confirm") {
    if (!field.n) return
    if (!field.v) field.v = "";
    menu_link.click(function(){ toast_confirm_show(field, function(){ send_val(field, field.v); menu_close(); return false; }) });
  } else if (field.t == "submit") {
    if (!field.n) return
    if (!field.v) field.v = "";
    menu_link.click(function(){ send_val_submit(field, field.v); menu_close(); return false; });
  } else if (field.t == "submit_confirm") {
    if (!field.n) return
    if (!field.v) field.v = "";
    menu_link.click(function(){ toast_confirm_show(field, function(){ send_val_submit(field, field.v); menu_close(); return false; }); });
  } else if (field.t == "cmd") {
    menu_link.click(function(){ menu_close(); cmd_execute(field.cmd); return false; });
  } else if (field.t == "link") {
    if (!field.de) field.de = field.c;
    var de = field.de;
    if (de.startsWith(":")) de = window.location.protocol + "//" + window.location.hostname + de; 
    menu_link.attr("href", de);
    if (field.w) menu_link.attr("target", field.w);
  } else if (field.t == "page") {
    if (!field.v) field.v = "";
    if (field.m == "fix") {
      if (field.v) {
        tmp_menu.click(function(){ send_val(field, field.v); page_show(i); menu_close(); return false; });
      } else {
        tmp_menu.click(function(){ page_show(i); menu_close(); return false; });
      }
    } else {
      if (field.v) {
        menu_link.click(function(){ send_val(field, field.v); page_show(i); menu_close(); return false; });
      } else {
        menu_link.click(function(){ page_show(i); menu_close(); return false; });
      }
    }
    tmp_menu.attr("data-type", "pages");
    tmp_menu.attr("data-pages", i);
  } else if (field.t == "popup") {
    if (!field.v) field.v = "";

    if (field.m == "fix") {
      if (field.v) {
        tmp_menu.click(function(){ send_val(field, field.v); popup_show(i); menu_close(); return false; });
      } else {
        tmp_menu.click(function(){ popup_show(i); menu_close(); return false; });
      }
    } else {
      if (field.v) {
        menu_link.click(function(){ send_val(field, field.v); popup_show(i); menu_close(); return false; });
      } else {
        menu_link.click(function(){ popup_show(i); menu_close(); return false; });
      }
    }
  } else if (field.t == "slider") {
    if (!field.n) return

    cfg.data_fields.push(field.n);
    tmp_menu = $("#tmp_menu_slider").clone();
    tmp_menu.removeAttr("id");
    tmp_menu.attr("data-name", field.n);
    tmp_menu.attr("data-type", field.t);
    if (field.vt) tmp_menu.attr("data-value-type", field.vt);

    var inp = tmp_menu.find(".in");
    attr_inp_num(field, inp)
    if (field.v) inp.val(field.v);

    inp.on("change", function() {
      send_val_delay(field, $(this).val());
    });
  } else if (field.t == "select") {
    if (!field.n) return

    cfg.data_fields.push(field.n);
    tmp_menu = $("#tmp_menu_select").clone();
    tmp_menu.removeAttr("id");
    tmp_menu.attr("data-name", field.n);
    tmp_menu.attr("data-type", field.t);
    if (field.vt) tmp_menu.attr("data-value-type", field.vt);

    var inp = tmp_menu.find(".in");
    if (field.mu) inp.attr("multiple", field.mu);
    if (field.vs) {
      field.vs = val_to_array(field.vs);
      for (var i = 0; i < field.vs.length; i++) {
        var v = field.vs[i].split(cfg.main.delimiter_val);
        var option = $("#tmp_select_option").clone();
        option.removeAttr("id");
        if (v[1]) {
          option.attr("value", v[0]);
          v[0] = v[1];
        } else if (field.m == "string") {
          option.attr("value", v[0]);
         } else {
          option.attr("value", i);
        }
        option.text(v[0]);
        inp.append(option);
      }
    }

    if (field.v) inp.val(field.v);

    inp.change(function() {
      send_val(field, this.value);
    });
  }

  var view = true;
  if (field.st) if (!val_to_bool(field.st)) view = false;
  if (view) {
    if (field.m == "fix") {
      $(".m-burger").before(tmp_menu);
    } else {
      $(".pages").append(tmp_menu);
    }
  }
}


function add(field, target, type = "") {
  if (type == "" && field.t) {
    type = field.t;
  } else if (typeof(field) === "string") {
    type = field;
    field = {};
  }

  if (type.startsWith("value_")) {
    type = type.replace("value_", "");
    field.t = type;
  }

  if (field.n && (!field.vt || field.vt == "remote" || field.vt == "both")) cfg.data_fields.push(field.n);
  if (field.d) cfg.data_fields.push(field.d);

  if (type == "abort") {
    add_abort(field, target);
  } else if (type == "abort_confirm") {
    add_abort_confirm(field, target);
  } else if (type == "button") {
    add_button(field, target);
  } else if (type == "buttongroup") {
    add_buttongroup(field, target);
  } else if (type == "card") {
    add_field(field, target);
  } else if (type == "cardgroup") {
    add_fieldgroup(field, target);
  } else if (type == "checkbox") {
    add_checkbox(field, target);
  } else if (type == "checkboxslider" || type == "bool") {
    field.t = "checkboxslider";
    add_checkboxslider(field, target);
  } else if (type == "color") {
    add_color(field, target);
  } else if (type == "colorpalette") {
    add_colorpalette(field, target);
  } else if (type == "colorpicker") {
    add_colorpicker(field, target);
  } else if (type == "colorslider") {
    add_colorslider(field, target);
  } else if (type == "confirm") {
    add_confirm(field, target);
  } else if (type == "date") {
    add_date(field, target);
  } else if (type == "editor") {
    add_editor(field, target);
  } else if (type == "editor_code") {
    add_editor_code(field, target);
  } else if (type == "email") {
    add_email(field, target);
  } else if (type == "fieldset") {
    add_field(field, target);
  } else if (type == "fieldsetgroup") {
    add_fieldgroup(field, target);
  } else if (type == "file") {
    add_file(field, target);
  } else if (type == "group") {
    add_group(field, target);
  } else if (type == "group_container") {
    add_group_container(field, target);
  } else if (type == "hidden") {
    add_hidden(field, target);
  } else if (type == "html") {
    add_html(field, target);
  } else if (type == "icon") {
    add_icon(field, target);
  } else if (type == "iframe") {
    add_iframe(field, target);
  } else if (type == "image" || type == "picture") {
    field.t = "image";
    add_image(field, target);
  } else if (type == "label") {
    add_label(field, target);
  } else if (type == "link") {
    add_link(field, target);
  } else if (type == "linkbutton") {
    add_linkbutton(field, target);
  } else if (type == "live") {
    add_live(field, target);
  } else if (type == "month") {
    add_month(field, target);
  } else if (type == "nav") {
    add_nav(field, target);
  } else if (type == "number" || type == "int") {
    field.t = "number";
    add_number(field, target);
  } else if (type == "numberslider" || type == "intslider") {
    field.t = "numberslider";
    add_numberslider(field, target);
  } else if (type == "password") {
    add_password(field, target);
  } else if (type == "passwordverify") {
    add_passwordverify(field, target);
  } else if (type == "progress") {
    add_progress(field, target);
  } else if (type == "radio") {
    add_radio(field, target);
  } else if (type == "radiogroup") {
    add_radiogroup(field, target);
  } else if (type == "raw") {
    add_raw(field, target);
  } else if (type == "search") {
    add_search(field, target);
  } else if (type == "section") {
    add_section(field, target);
  } else if (type == "select") {
    add_select(field, target);
  } else if (type == "selectbutton") {
    add_selectbutton(field, target);
  } else if (type == "selectlist") {
    add_selectlist(field, target);
  } else if (type == "slider" || type == "range") {
    field.t = "slider";
    add_slider(field, target);
  } else if (type == "slide") {
    add_slide(field, target);
  } else if (type == "slide_container") {
    add_slide_container(field, target);
  } else if (type == "space") {
    add_space(field, target);
  } else if (type == "status") {
    add_status(field, target);
  } else if (type == "submit") {
    add_submit(field, target);
  } else if (type == "submit_confirm") {
    add_submit_confirm(field, target);
  } else if (type == "switch") {
    add_switch(field, target);
  } else if (type == "tabgroup") {
    add_tabgroup(field, target);
  } else if (type == "tabgroup_container") {
    add_tabgroup_container(field, target);
  } else if (type == "tabgroup_nav") {
    add_tabgroup_nav(field, target);
  } else if (type == "table") {
    add_table(field, target);
  } else if (type == "tel") {
    add_tel(field, target);
  } else if (type == "text" || type == "string") {
    field.t = "text";
    add_text(field, target);
  } else if (type == "textbutton" || type == "stringbutton") {
    field.t = "textbutton";
    add_textbutton(field, target);
  } else if (type == "textarea") {
    add_textarea(field, target);
  } else if (type == "time") {
    add_time(field, target);
  } else if (type == "toggle") {
    add_toggle(field, target);
  } else if (type == "test") {
    add_test(field, target);
  } else if (type == "txt" || type == "value") {
    field.t = "txt";
    add_txt(field, target);
  } else if (type == "url") {
    add_url(field, target);
  } else if (type == "week") {
    add_week(field, target);
  } else if (type == "wizard") {
    add_wizard(field, target);
  } else if (type == "wizard_container") {
    add_wizard_container(field, target);
  }
}


function add_button(field, target) {
  if (!field.n) return;

  attr_vs(field, ["True"]);

  if(!field.v) field.v = field.vs[0][0];

  var tmp = $("#tmp_button").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.c) {
    inp.html(field.c);
  } else {
    inp.html(field.vs[0][1]);
  }
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));

  if (field.n && field.v) {
    inp.click(function() {
      send_val(field, field.v);
    });
  } else if (field.n) {
    inp.click(function() {
      send_val(field, "");
    });
  }

  target.append(tmp);
}


function add_buttongroup(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_buttongroup").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_is(field);
  if (field.vs) {
    field.vs = val_to_array(field.vs);
    for (var i = 0; i < field.vs.length; i++) {
      var v = field.vs[i].split(cfg.main.delimiter_val);
      var option = $("#tmp_buttongroup_button").clone();
      if (v[1]) {
        option.attr("value", v[0]);
        v[0] = v[1];
      } else if (field.m == "string") {
        option.attr("value", v[0]);
      } else {
        option.attr("value", i);
      }
      if (field.di) option.attr("disabled", true);
      option.html(v[0]);
      if (field.is) if (field.is[i]) option.prepend(add_icon_inline(field.is[i]));
      option.click(function() {
        send_val(field, this.value);
      });
      inp.append(option);
    }
  }

  target.append(tmp);
}


function add_caption_r(field, target, val) {
  target.next(".caption_error").remove();
  if (val) {
    if (field.r_ca) {
      val = field.r_ca;
    } else if (cfg["r_cad"][field.t]) {
      val = cfg["r_cad"][field.t];
    } else if (cfg["r_cad"]["*"]) {
      val = cfg["r_cad"]["*"];
    } else {
      val = "";
    }

    if (val != "") {
      var tmp = $("#tmp_caption_error").clone();
      tmp.removeAttr("id");
      tmp.html(val);
      target.after(tmp);
    }
  }
}


function add_caption_pa(field, target, val) {
  target.next(".caption_error").remove();
  if (val) {
    if (field.pa_ca) {
      val = field.pa_ca;
    } else if (cfg["pa_cad"][field.t]) {
      val = cfg["pa_cad"][field.t];
    } else if (cfg["pa_cad"]["*"]) {
      val = cfg["pa_cad"]["*"];
    } else {
      val = "";
    }

    if (val != "") {
      var tmp = $("#tmp_caption_error").clone();
      tmp.removeAttr("id");
      tmp.html(val);
      target.after(tmp);
    }
  }
}


function add_checkbox(field, target) {
  if (!field.n) return;

  attr_vs(field);

  var tmp = $("#tmp_checkbox").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);

  if (field.vs) {
    tmp.attr("data-values", field.vs);
    attr_vs(field);
     if (field.v) {
      if (field.v.toLowerCase() == field.vs[1][0].toLowerCase()) inp.prop("checked", true);
    }
  } else {
    attr_vs(field);
    if (field.v) {
      field.v = val_to_bool(field.v);
      inp.prop("checked", field.v ? true : false);
    }
  }
  
  inp.on("click", function() {
    send_val(field, $(this).is(":checked") ? field.vs[1][0] : field.vs[0][0]);
  });

  target.append(tmp);
}


function add_checkboxslider(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_checkboxslider").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);

  if (field.vs) {
    tmp.attr("data-values", field.vs);
    attr_vs(field);
     if (field.v) {
      if (field.v.toLowerCase() == field.vs[1][0].toLowerCase()) inp.prop("checked", true);
    }
  } else {
    attr_vs(field);
    if (field.v) {
      field.v = val_to_bool(field.v);
      inp.prop("checked", field.v ? true : false);
    }
  }

  inp.on("click", function() {
    send_val(field, $(this).is(":checked") ? field.vs[1][0] : field.vs[0][0]);
  });

  target.append(tmp);
}


function add_color(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_color").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_colorpalette(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_colorpalette").clone();
  attr_frm(field, tmp);

  var btns = tmp.find(".btn-color");

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  btns.each(function(i, btn) {
    if (field.di) btn.attr("disabled", true);
    if (field.s) btn.attr("style", field.s);
    $(btn).click(function() {
       var rgb = $(this).css("backgroundColor");
       send_val(field, val_rgb_to_hex(rgb));
    });
  });

  target.append(tmp);
}


function add_colorpicker(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_colorpicker").clone();
  attr_frm(field, tmp);

  var inp = tmp.find(".in");
  attr_inp(field, inp);

  target.append(tmp);
  
  input_colorpicker_field = field;
}


function add_colorslider(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_colorslider").clone();
  attr_frm(field, tmp);

  var id = field.n;

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var lbl_r = tmp.find(".lbl-r");
  lbl_r.text(field.l_r);
  
  var lbl_g = tmp.find(".lbl-g");
  lbl_g.text(field.l_g);
  
  var lbl_b = tmp.find(".lbl-b");
  lbl_b.text(field.l_b);

  var id = field.n;

  var inp_r = tmp.find(".in-r");
  var inp_g = tmp.find(".in-g");
  var inp_b = tmp.find(".in-b");

  if (field.di) inp_r.attr("disabled", true);
  if (field.s) inp_r.attr("style", field.s);

  if (field.di) inp_g.attr("disabled", true);
  if (field.s) inp_g.attr("style", field.s);

  if (field.di) inp_b.attr("disabled", true);
  if (field.s) inp_b.attr("style", field.s);

  attr_inp_num(field, inp_r)
  if (field.di) inp_r.attr("disabled", true);
  if (field.s) inp_r.attr("style", field.s);

  attr_inp_num(field, inp_g);
  if (field.di) inp_g.attr("disabled", true);
  if (field.s) inp_g.attr("style", field.s);

  attr_inp_num(field, inp_b);
  if (field.di) inp_b.attr("disabled", true);
  if (field.s) inp_b.attr("style", field.s);

  if (field.v) {
    var comp = val_hex_to_rgb_comp(field.v);
    inp_r.val(comp.r);
    inp_g.val(comp.g);
    inp_b.val(comp.b);
  }

  inp_r.on("change", function() {
    send_val_delay(field, val_rgb_comp_to_hex(inp_r.val(), inp_g.val(), inp_b.val()));
  });

  inp_g.on("change", function() {
   send_val_delay(field, val_rgb_comp_to_hex(inp_r.val(), inp_g.val(), inp_b.val()));
  });

  inp_b.on("change", function() {
    send_val_delay(field, val_rgb_comp_to_hex(inp_r.val(), inp_g.val(), inp_b.val()));
  });

  target.append(tmp);
}


function add_confirm(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_confirm").clone();
  attr_frm(field, tmp);;

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.c) inp.html(field.c);
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));

  if (field.n && field.v) {
    if (field.msg) {
      inp.click(function() {
        toast_confirm_show(field, function(){ send_val(field, field.v); });
      });
    } else {
      inp.click(function() {
        send_val(field, field.v);
      });
    }
  } else if (field.n) {
    if (field.msg) {
      inp.click(function() {
        toast_confirm_show(field, function(){ send_val(field, ""); });
      });
    } else {
      inp.click(function() {
        send_val(field, "");
      });
    }
  }

  target.append(tmp);
}


function add_date(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_date").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_num(field, inp)
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_editor(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_editor").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.rows) inp.attr("rows", field.rows);
  if (field.cols) inp.attr("cols", field.cols);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val().replace(/\n/g, '\n' ), $(this));
  });

  target.append(tmp);
}



function add_editor_code(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_editor_code").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.rows) inp.attr("rows", field.rows);
  if (field.cols) inp.attr("cols", field.cols);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val().replace(/\n/g, '\n' ), $(this));
  });

  target.append(tmp);
}


function add_email(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_email").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_field(field, target) {
  target.removeAttr("id");
  attr_view(field, target);
  attr_space(field, target);

  var header = target.find(".header");
  if (field.cl) header.addClass(field.cl);
  if (field.cl_h) header.addClass(field.cl_h);
  if (field.s) header.attr("style", field.s);
  if (field.st) {
    if (val_to_bool(field.st)) {
      target.find(".header").addClass("active");
    } else {
      target.find(".body").addClass("hide");
    }
    header.click(function() {
      if (set_field_toggle(target)) {
        if (field.cmd) cmd_execute(field.cmd);
        if (field.get) data_get(field.get);
        if (field.set) data_get(field.set);
      }
    });
  }

  header.html(field.l);
  if (field.i) header.prepend(add_icon_inline(field.i));

  var body = target.find(".body");
  if (field.c) body.html(field.c);
  if (field.cl_c) body.addClass(field.cl_c);
}


function add_fieldgroup(field, target) {
  target.removeAttr("id");
  attr_view(field, target);
  attr_space(field, target);
  target.attr("data-group", field.group);
  target.attr("data-group-index", field.group_index);

  var header = target.find(".header");
  if (field.cl) header.addClass(field.cl);
  if (field.cl_h) header.addClass(field.cl_h);
  if (field.s) header.attr("style", field.s);
  header.click(function() {
    if (field.cmd) cmd_execute(field.cmd);
    if (field.get) data_get(field.get);
    if (field.set) data_get(field.set);
    set_fieldgroup_toggle(target);
  });

  header.html(field.l);
  if (field.i) header.prepend(add_icon_inline(field.i));
  if (field.group_index == 0) header.addClass("inactive");

  var body = target.find(".body");
  if (field.c) body.html(field.c);
  if (field.cl_c) body.addClass(field.cl_c);
  if (field.group_index > 0) body.addClass("hide");
}


function add_file(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_file").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.c) inp.attr("accept", field.c);

  inp.change(function() {
    send_upload(field, $(this));
  });

  target.append(tmp);
}


function add_group(field, target) {
  target.removeAttr("id");
}


function add_group_container(field, target) {
  target.removeAttr("id");
  attr_view(field, target);
  attr_space(field, target);

  var header = target.find(".header_container");
  if (field.cl) header.addClass(field.cl);
  if (field.cl_h) header.addClass(field.cl_h);
  if (field.s) header.attr("style", field.s);
  if (field.st) {
    if (val_to_bool(field.st)) {
      target.find(".header_container").addClass("active");
    } else {
      target.find(".bodys").addClass("hide");
    }
    header.click(function() {
      set_group_toggle(target);
    });
  }

  header.html(field.l);
  if (field.i) header.prepend(add_icon_inline(field.i));

  var body = target.find(".bodys");
  if (field.c) body.prepend(field.c);
  if (field.cl_c) body.addClass(field.cl_c);
}


function add_hidden(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_hidden").clone();
  attr_frm(field, tmp);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  target.append(tmp);
}


function add_html(field, target) {
  var tmp = $("#tmp_html").clone();
  attr_frm(field, tmp);
  if (field.max) tmp.attr("data-max", field.max);
  if (field.vs) tmp.attr("data-values", field.vs);
  tmp.html(attr_vs_content(field.c, field.vs));
  if (field.s) tmp.attr("style", field.s);

  target.append(tmp);
}


function add_icon(field, target) {
  var tmp = $("#tmp_icon").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  if (field.vs) tmp.attr("data-values", field.vs);
  if (field.c) inp.prepend(add_icon_inline(attr_vs_content(field.c, field.vs)));

  if (field.s) inp.attr("style", field.s);
  if (field.wi) inp.attr("width", field.wi);
  if (field.he) inp.attr("height", field.he);

  target.append(tmp);
}


function add_icon_inline(icon) {
  if (icon == "") return "";
  if (icon.indexOf("<") !== -1 && icon.indexOf(">") !== -1) {
    return icon;
  } else if (icon.indexOf(".") !== -1) {
    var tmp_icon = $("#tmp_icon_inline_file").clone();
    tmp_icon.attr("src", cfg.main.url_icon + icon);
  } else if (icon.length > 5) {
    var tmp_icon = $("#tmp_icon_inline_font").clone();
    tmp_icon.addClass(icon);
  } else {
    var tmp_icon = $("#tmp_icon_inline").clone();
    tmp_icon.html("&#" + icon + ";");
  }
  tmp_icon.removeAttr("id");
  return tmp_icon;
}


function add_iframe(field, target) {
  var tmp = $("#tmp_iframe").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  inp.attr("src", field.c);
  if (field.s) inp.attr("style", field.s);
  if (field.wi) inp.attr("width", field.wi);
  if (field.he) inp.attr("height", field.he);

  target.append(tmp);
}


function add_image(field, target) {
  var tmp = $("#tmp_image").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  if (field.vs) tmp.attr("data-values", field.vs);
  if (field.c) {
    cont = attr_vs_content(field.c, field.vs);
    if (cont.indexOf("http") !== -1 || cont.startsWith(cfg.main.url_images) || cont.startsWith("../")) {
      inp.attr("src", cont);
    } else {
      inp.attr("src", cfg.main.url_images + cont);
    }
  }
  if (field.s) inp.attr("style", field.s);
  if (field.wi) inp.attr("width", field.wi);
  if (field.he) inp.attr("height", field.he);

  target.append(tmp);
}


function add_label(field, target) {
  var tmp = $("#tmp_label").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  if (field.s) lbl.attr("style", field.s);
  if (field.max) tmp.attr("data-max", field.max);
  if (field.vs) tmp.attr("data-values", field.vs);
  lbl.text(attr_vs_content(field.c, field.vs));
  if (field.i) lbl.prepend(add_icon_inline(field.i));

  target.append(tmp);
}


function add_link(field, target) {
  var tmp = $("#tmp_link").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  inp.html(field.c);
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));
  if (field.s) inp.attr("style", field.s);
  if (field.w) inp.attr("target", field.w);
  if (field.de) {
    var de = field.de;
    if (de.startsWith(":")) de = window.location.protocol + "//" + window.location.hostname + de; 
    inp.attr("href", field.de);
  }

  target.append(tmp);
}


function add_linkbutton(field, target) {
  var tmp = $("#tmp_linkbutton").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  inp.html(field.c);
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));
  if (field.s) inp.attr("style", field.s);
  if (field.w) inp.attr("target", field.w);
  if (field.de) {
    var de = field.de;
    if (de.startsWith(":")) de = window.location.protocol + "//" + window.location.hostname + de; 
    inp.attr("href", field.de);
  }
  target.append(tmp);
}


function add_live(field, target) {
  var tmp = $("#tmp_live").clone();
  attr_frm(field, tmp);
  target.append(tmp);
}


function add_month(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_month").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_num(field, inp)
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_nav(field, target) {
  if (!field.n) return;

  attr_vs(field, ["off=<", "on=>"]);

  var tmp = $("#tmp_nav").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var btn_prev = tmp.find(".btn-prev");
  var btn_next = tmp.find(".btn-next");

  if (field.di) btn_prev.attr("disabled", true);
  if (field.di) btn_next.attr("disabled", true);
  if (field.s) btn_prev.attr("style", field.s);
  if (field.s) btn_next.attr("style", field.s);
  if (field.prev) {
    btn_prev.html(field.prev);
  } else {
    btn_prev.html(field.vs[0][1]);
  }
  if (field.next) {
    btn_next.html(field.next);
  } else {
    btn_next.html(field.vs[1][1]);
  }

  btn_prev.click(function() {
    send_val(field, field.vs[0][0]);
  });

  btn_next.click(function() {
    send_val(field, field.vs[1][0]);
  });

  target.append(tmp);
}


function add_number(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_number").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_num(field, inp)
  if (field.ph) inp.attr("placeholder", field.ph);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_numberslider(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_numberslider").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  var slider = tmp.find(".slider");
  if (field.di) inp.attr("disabled", true);
  if (field.di) slider.attr("disabled", true);
  if (field.s) inp.attr("style", field.s);
  if (field.s) slider.attr("style", field.s);
  attr_inp_num(field, inp);
  attr_inp_num(field, slider);
  if (field.ph) inp.attr("placeholder", field.ph);
  if (field.v) {
    inp.val(field.v);
    slider.val(field.v);
  }

  slider.on("change mousemove", function() {
    inp.val($(this).val());
  });

  slider.on("change", function() {
    var val = $(this).val();
    inp.val(val);
    send_val_delay(field, val);
  });

  inp.on("change", function() {
    var val = $(this).val();
    slider.val(val);
    send_val_delay(field, val, $(this));
  });

  target.append(tmp);
}


function add_password(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_password").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_passwordverify(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_passwordverify").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  field.inp_1 = tmp.find(".in-1");
  attr_inp(field, field.inp_1);
  attr_inp_str(field, field.inp_1);

  field.inp_2 = tmp.find(".in-2");
  attr_inp(field, field.inp_2);
  attr_inp_str(field, field.inp_2);

  if (field.v) {
    field.inp_1.val(field.v);
    field.inp_2.val(field.v);
  }

  field.inp_1.on("change", function() {
    if (field.pa) {
      if (field.inp_1.val().match(field.pa)) {
        $(this).removeClass("invalid");
      } else {
        $(this).addClass("invalid");
      }
    }

    if (field.inp_1.val() == field.inp_2.val()) {
      field.inp_2.removeClass("invalid");
      send_val_delay(field, $(this).val());
    } else {
      field.inp_2.addClass("invalid");
    }
  });

  field.inp_2.on("change", function() {
    if (field.inp_1.val() == field.inp_2.val()) {
      field.inp_2.removeClass("invalid");
      send_val_delay(field, $(this).val());
    } else {
      field.inp_2.addClass("invalid");
    }
  });

  target.append(tmp);
}


function add_progress(field, target) {
  var tmp = $("#tmp_progress").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  if (field.cl)inp.addClass(field.cl);
  if (field.cl_c)inp.addClass(field.cl_c);
  if (field.v) {
    inp.attr("style", "width:" + field.v + "%");
    inp.html(field.v + "%");
  }

  target.append(tmp);
}


function add_radio(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_radio").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_is(field);
  if (field.vs) {
    field.vs = val_to_array(field.vs);
    for (var i = 0; i < field.vs.length; i++) {
      var v = field.vs[i].split(cfg.main.delimiter_val);
      var option = $("#tmp_radio_input").clone();
      option.attr("id", field.n + "-" + i);
      option.attr("name", field.n);
      if (v[1]) {
        option.attr("value", v[0]);
        if (field.v == v[0]) option.prop("checked", true);
        v[0] = v[1];
      } else if (field.m == "string"){
        option.attr("value", v[0]);
        if (field.v == v[0]) option.prop("checked", true);
      } else {
        option.attr("value", i);
        if (field.v == i) option.prop("checked", true);
      }
      if (field.di) option.attr("disabled", true);
      var lbl = $("#tmp_radio_label").clone();
      lbl.removeAttr("id");
      lbl.attr("for", field.n + "-" + i);
      lbl.text(v[0]);
      if (field.is) if (field.is[i]) lbl.prepend(add_icon_inline(field.is[i]));
      var span = $("#tmp_radio_checkmark").clone();
      span.removeAttr("id");
      lbl.append(option);
      lbl.append(span);
      inp.append(lbl);
    }
  }

  inp.change(function() {
    send_val_delay(field, $("input:checked", this).val());
  });

  target.append(tmp);
}


function add_radiogroup(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_radiogroup").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_is(field);
  if (field.vs) {
    field.vs = val_to_array(field.vs);
    for (var i = 0; i < field.vs.length; i++) {
      var v = field.vs[i].split(cfg.main.delimiter_val);
      var option = $("#tmp_radiogroup_input").clone();
      option.attr("id", field.n + "-" + i);
      option.attr("name", field.n);
      if (v[1]) {
        option.attr("value", v[0]);
        if (field.v == v[0]) option.prop("checked", true);
        v[0] = v[1];
      } else if (field.m == "string") {
        option.attr("value", v[0]);
        if (field.v == v[0]) option.prop("checked", true);
      } else {
        option.attr("value", i);
        if (field.v == i) option.prop("checked", true);
      }
      if (field.di) option.attr("disabled", true);
      var lbl = $("#tmp_radiogroup_label").clone();
      lbl.removeAttr("id");
      lbl.attr("for", field.n + "-" + i);
      lbl.text(v[0]);
      if (field.is) if (field.is[i]) lbl.prepend(add_icon_inline(field.is[i]));
      inp.append(option);
      inp.append(lbl);
    }
  }

  inp.change(function() {
    send_val_delay(field, $("input:checked", this).val());
  });

  target.append(tmp);
}


function add_raw(field, target) {
  target.append(field.c);
}


function add_search(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_search").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_section(field, target) {
  var tmp = $("#tmp_section").clone();
  attr_frm(field, tmp);
  if (field.s) tmp.attr("style", field.s);

  target.append(tmp);
}


function add_select(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_select").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.ph) inp.attr("placeholder", field.ph);
  if (field.mu) inp.attr("multiple", field.mu);
  if (field.vs) {
    field.vs = val_to_array(field.vs);
    for (var i = 0; i < field.vs.length; i++) {
      var v = field.vs[i].split(cfg.main.delimiter_val);
      var option = $("#tmp_select_option").clone();
      option.removeAttr("id");
      if (v[1]) {
        option.attr("value", v[0]);
        v[0] = v[1];
      } else if (field.m == "string") {
        option.attr("value", v[0]);
       } else {
        option.attr("value", i);
      }
      option.text(v[0]);
      inp.append(option);
    }
  }

  if (field.v) inp.val(field.v);

  inp.change(function() {
    send_val(field, $(this).val());
  });

  target.append(tmp);
}


function add_selectbutton(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_selectbutton").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.ph) inp.attr("placeholder", field.ph);
  if (field.mu) inp.attr("multiple", field.mu);
  if (field.vs) {
    field.vs = val_to_array(field.vs);
    for (var i = 0; i < field.vs.length; i++) {
      var v = field.vs[i].split(cfg.main.delimiter_val);
      var option = $("#tmp_select_option").clone();
      option.removeAttr("id");
      if (v[1]) {
        option.attr("value", v[0]);
        v[0] = v[1];
      } else if (field.m == "string") {
        option.attr("value", v[0]);
      } else {
        option.attr("value", i);
      }
      option.text(v[0]);
      inp.append(option);
    }
  }

  if (field.v) inp.val(field.v);

  inp.change(function() {
    send_val(field, this.value);
  });

  var btn_prev = tmp.find(".btn-prev");
  var btn_next = tmp.find(".btn-next");

  if (field.di) btn_prev.attr("disabled", true);
  if (field.di) btn_next.attr("disabled", true);

  btn_prev.click(function() {
    var val = inp.find("option:selected").index();
    var count = inp.find("option").length;
    val--;
    if (val < 0) val = count - 1;
    inp.val(val);
    send_val(field, inp.val());
  });

  btn_next.click(function() {
    var val = inp.find("option:selected").index();
    var count = inp.find("option").length;
    val++;
    if (val >= count) val = 0;
    inp.val(val);
    send_val(field, inp.val());
  });

  target.append(tmp);
}


function add_selectlist(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_selectlist").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.ph) inp.attr("placeholder", field.ph);
  if (field.mu) inp.attr("multiple", field.mu);
  if (field.vs) {
    field.vs = val_to_array(field.vs);
    inp.attr("size", field.vs.length);
    for (var i = 0; i < field.vs.length; i++) {
      var v = field.vs[i].split(cfg.main.delimiter_val);
      var option = $("#tmp_select_option").clone();
      option.removeAttr("id");
      if (v[1]) {
        option.attr("value", v[0]);
        v[0] = v[1];
      } else if (field.m == "string") {
        option.attr("value", v[0]);
      } else {
        option.attr("value", i);
      }
      option.text(v[0]);
      inp.append(option);
    }
  }

  if (field.v) inp.val(field.v);

  inp.change(function() {
    send_val(field, $(this).val());
  });

  target.append(tmp);
}


function add_slider(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_slider").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_num(field, inp)
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val());
  });

  target.append(tmp);
}


function add_slide(field, target) {
  target.removeAttr("id");

  var header = target.find(".header");
  if (field.cl) header.addClass(field.cl);
  if (field.cl_h) header.addClass(field.cl_h);
  if (field.s) header.attr("style", field.s);
  header.html(field.l);
  if (field.i) header.prepend(add_icon_inline(field.i));

  var body = target.find(".body");
  if (field.c) body.html(field.c);
  if (field.cl_c) body.addClass(field.cl_c);
}


function add_slide_container(field, target) {
  target.removeAttr("id");
  attr_view(field, target);
  attr_space(field, target);

  target.find(".btn-prev").click(function() { slide_switch(field, target, -1); });
  target.find(".btn-next").click(function() { slide_switch(field, target, 1); });

  var footer = target.find(".footer");
  target.find(".slide").each(function(key, obj) {
    var tmp = $("#tmp_slide_status").clone();
    tmp.removeAttr("id");
    tmp.click(function() { slide_show(field, target, key); });
    footer.append(tmp);
  });

  slide_show(field, target, 0);
}


function add_space(field, target) {
  var tmp = $("#tmp_space").clone();
  attr_frm(field, tmp);

  var style = "";
  if (field.s) style = style + field.s;
  if (field.wi) style = style + "width:" + field.wi + ";";
  if (field.he) style = style + "height:" + field.he + ";";
  if (style != "") tmp.attr("style", style);

  target.append(tmp);
}


function add_submit(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_button").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.c) inp.html(field.c);
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));

  if (field.n && field.v) {
    inp.click(function() {
      send_val_submit(field, field.v);
    });
  } else if (field.n) {
    inp.click(function() {
      send_val_submit(field, "");
    });
  }

  target.append(tmp);
}


function add_submit_confirm(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_confirm").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.c) inp.html(field.c);
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));

  if (field.n && field.v) {
    if (field.msg) {
      inp.click(function() {
        toast_confirm_show(field, function(){ send_val_submit(field, field.v); });
      });
    } else {
      inp.click(function() {
        send_val_submit(field, field.v);
      });
    }
  } else if (field.n) {
    if (field.msg) {
      inp.click(function() {
        toast_confirm_show(field, function(){ send_val_submit(field, ""); });
      });
    } else {
      inp.click(function() {
        send_val_submit(field, "");
      });
    }
  }

  target.append(tmp);
}


function add_abort(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_button").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.c) inp.html(field.c);
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));

  if (field.n && field.v) {
    inp.click(function() {
      send_val_abort(field, field.v);
    });
  } else if (field.n) {
    inp.click(function() {
      send_val_abort(field, "");
    });
  }

  target.append(tmp);
}


function add_abort_confirm(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_confirm").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.c) inp.html(field.c);
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));

  if (field.n && field.v) {
    if (field.msg) {
      inp.click(function() {
        toast_confirm_show(field, function(){ send_val_abort(field, field.v); });
      });
    } else {
      inp.click(function() {
        send_val_abort(field, field.v);
      });
    }
  } else if (field.n) {
    if (field.msg) {
      inp.click(function() {
        toast_confirm_show(field, function(){ send_val_abort(field, ""); });
      });
    } else {
      inp.click(function() {
        send_val_abort(field, "");
      });
    }
  }

  target.append(tmp);
}


function add_status(field, target) {
  if (!field.n) return;

  attr_vs(field);

  var tmp = $("#tmp_status").clone();
  attr_frm(field, tmp);

  attr_lbl(field, tmp.find(".lbl"));

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_is(field);
  if (field.vs) {
    for (var i = 0; i < field.vs.length; i++) {
      var lbl = $("#tmp_status_label").clone();
      lbl.attr("data-value", field.vs[i][0]);
      lbl.text(field.vs[i][1]);
      if (field.v == field.vs[i][0]) lbl.addClass("active");
      if (field.is) {
        if (field.is[i]) {
          var v = field.is[i].split(cfg.main.delimiter_val);
          lbl.prepend(add_icon_inline(v[1]));
        }
      }
      inp.append(lbl);
    }
  }

  target.append(tmp);
}


function add_switch(field, target) {
  if (!field.n) return;

  attr_vs(field);

  var tmp = $("#tmp_switch").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var btn_on = tmp.find(".btn-on");
  var btn_off = tmp.find(".btn-off");

  if (field.di) btn_on.attr("disabled", true);
  if (field.di) btn_off.attr("disabled", true);
  
  if (field.s) btn_on.attr("style", field.s);
  if (field.s) btn_off.attr("style", field.s);

  if (field.v) field.v = val_to_bool(field.v);

  if (field.c) {
    field.c = val_to_array(field.c);
    if (field.c[0]) btn_off.html(field.c[0]);
    if (field.c[1]) btn_on.html(field.c[1]);
  } else if (field.vs) {
    if (field.vs[0][1]) btn_off.html(field.vs[0][1]);
    if (field.vs[1][1]) btn_on.html(field.vs[1][1]);
  }

  attr_class_switch(btn_on, field.v);
  attr_class_switch(btn_off, field.v, "btn-primary", "btn-default");

  btn_on.click(function() {
    set_switch_val(field, btn_on, btn_off, 1)
  });
  btn_off.click(function() {
    set_switch_val(field, btn_on, btn_off, 0)
  });

  target.append(tmp);
}


function add_tabgroup(field, target) {
  target.removeAttr("id");
  attr_view(field, target);

  if (field.c) target.html(field.c);
  if (field.cl_c) target.addClass(field.cl_c);

  target.attr("data-group", field.group);
  target.attr("data-group-index", field.group_index);

  if (field.group_index == 0) target.addClass("active");
}


function add_tabgroup_container(field, target) {
  target.removeAttr("id");
  attr_space(field, target);

  if (field.cl) target.addClass(field.cl);
  if (field.s) target.attr("style", field.s);

  var header = target.find(".header");
  if (field.l_h) header.html(field.l_h);
  if (field.i_h) header.prepend(add_icon_inline(field.i_h));
  if (header.html() == "") header.addClass("hide");
  if (field.st) {
    if (val_to_bool(field.st)) {
      target.find(".header").addClass("active");
    } else {
      target.find(".nav").addClass("hide");
      target.find(".bodys").addClass("hide");
    }
    header.click(function() {
      set_tabgroup_container_toggle(target);
    });
  }
}


function add_tabgroup_nav(field, target) {
  var tmp = $("#tmp_tabgroup_nav").clone();
  tmp.removeAttr("id");
  attr_view(field, tmp);

  var inp = tmp.find(".in");
  if (field.cl) inp.addClass(field.cl);
  if (field.cl_h) inp.addClass(field.cl_h);
  if (field.s) inp.attr("style", field.s);
  inp.html(field.l);
  if (field.i) inp.prepend(add_icon_inline(field.i));

  inp.attr("data-group", field.group);
  inp.attr("data-group-index", field.group_index);

  inp.click(function() {
    if (field.cmd) cmd_execute(field.cmd);
    if (field.get) data_get(field.get);
    if (field.set) data_get(field.set);
    set_tabgroup_toggle($(this)); 
  });

  if (field.group_index == 0) inp.addClass("active");

  target.append(tmp);
}


function add_table(field, target) {
  var tmp = $("#tmp_table").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find("table");
  if (field.s) inp.attr("style", field.s);
  if (field.cl) inp.attr("class", field.cl);

  if (field.c_h) {
    var count = 0;
    inp = tmp.find("thead");
    if (field.cl_h) inp.attr("class", field.cl_h);
    field.c_h = val_to_array(field.c_h, false);
    var str = "";
    jQuery.each(field.c_h, function(i, v) { str += "<th>" + v + "</th>"; count++; });
    inp.append("<tr>" + str + "</tr>");
    
    if (field.count) count = field.count;
    tmp.attr("data-count", count);
  }

  if (field.c) {
    inp = tmp.find("tbody");
    if (field.cl_b) inp.attr("class", field.cl_b);
    field.c = val_to_array(field.c, false);
    var str = "";
    jQuery.each(field.c_f, function(i, v) { str += "<td>" + v + "</td>";});
    inp.append("<tr>" + str + "</tr>");
  }

  if (field.c_f) {
    inp = tmp.find("tfoot");
    if (field.cl_f) inp.attr("class", field.cl_f);
    field.c_f = val_to_array(field.c_f, false);
    var str = "";
    jQuery.each(field.c_f, function(i, v) { str += "<th>" + v + "</th>";});
    inp.append("<tr>" + str + "</tr>");
  }

  target.append(tmp);
}


function add_tel(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_tel").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_text(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_text").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_textbutton(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_textbutton").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  var btn = tmp.find(".btn");
  if (field.di) btn.attr("disabled", true);
  if (field.c) btn.html(field.c);
  if (field.c_i) btn.prepend(add_icon_inline(field.c_i));

  btn.click(function() {
    send_val(field, inp.val());
  });

  target.append(tmp);
}


function add_textarea(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_textarea").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.rows) inp.attr("rows", field.rows);
  if (field.cols) inp.attr("cols", field.cols);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val().replace(/\n/g, '\n' ), $(this));
  });

  target.append(tmp);
}


function add_time(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_time").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_num(field, inp)
  if (field.ph) inp.attr("placeholder", field.ph);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_toggle(field, target) {
  if (!field.n) return;

  attr_vs(field);

  var tmp = $("#tmp_toggle").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  if (field.v) {
    field.v = val_to_bool(field.v);
  } else {
    field.v = 0;
  }

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  if (field.c) {
    inp.html(field.c);
  } else {
    inp.html(field.v ? field.vs[1][1] : field.vs[0][1]);
  }
  if (field.c_i) inp.prepend(add_icon_inline(field.c_i));

  inp.val(field.v);
  attr_class_switch(inp, field.v);

  inp.click(function() {
      var val = val_to_bool($(this).val())
      set_toggle_val(field, val_to_bool($(this).val()));
    });

  target.append(tmp);
}


function add_test(field, target) {
  var tmp = $("#tmp_test").clone();
  attr_frm(field, tmp);

  target.append(tmp);
}


function add_txt(field, target) {
  var tmp = $("#tmp_txt").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  if (field.max) tmp.attr("data-max", field.max);
  if (field.vs) tmp.attr("data-values", field.vs);
  inp.html(attr_vs_content(field.c, field.vs));
  if (field.s) inp.attr("style", field.s);

  target.append(tmp);
}


function add_url(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_url").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_str(field, inp);
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_week(field, target) {
  if (!field.n) return;

  var tmp = $("#tmp_week").clone();
  attr_frm(field, tmp);

  var lbl = tmp.find(".lbl");
  attr_lbl(field, lbl);

  var inp = tmp.find(".in");
  attr_inp(field, inp);
  attr_inp_num(field, inp)
  if (field.v) inp.val(field.v);

  inp.on("change", function() {
    send_val_delay(field, $(this).val(), $(this));
  });

  target.append(tmp);
}


function add_wizard(field, target) {
  target.removeAttr("id");
  attr_frm(field, target);
  attr_view(field, target);

  var header = target.find(".header");
  if (field.cl) header.addClass(field.cl);
  if (field.cl_h) header.addClass(field.cl_h);
  if (field.s) header.attr("style", field.s);
  header.html(field.l);
  if (field.i) header.prepend(add_icon_inline(field.i));

  var body = target.find(".body");
  if (field.c) body.html(field.c);
  if (field.cl_c) body.addClass(field.cl_c);
}


function add_wizard_container(field, target) {
  target.removeAttr("id");
  attr_view(field, target);
  attr_space(field, target);

  attr_vs(field, ["❮ Prev", "Next ❯", "Save"]);

  target.find(".btn-prev").html(field.vs[0][1]);
  target.find(".btn-next").html(field.vs[1][1]);
  target.find(".btn-submit").html(field.vs[2][1]);

  target.find(".btn-prev").click(function() { wizard_switch(field, target, -1); });
  target.find(".btn-next").click(function() { wizard_switch(field, target, 1); });
  target.find(".btn-submit").click(function() { wizard_switch(field, target, 1); });

  var footer = target.find(".footer");
  target.find(".wizard").each(function(key, obj) {
    var tmp = $("#tmp_wizard_status").clone();
    tmp.removeAttr("id");
    footer.append(tmp);
  });

  wizard_show(field, target, 0);
}


//attr
function attr_view(field, target) {
  if (field.vv) {
    target.attr("data-value-view", field.vv);
    target.addClass("hide");
  }
}


function attr_space(field, target) {
  if (field.sp) target.attr("style", "margin-top:"+ field.sp);
}


function attr_frm(field, target) {
  attr_space(field, target);
  target.removeAttr("id");
  if (field.n) target.attr("data-name", field.n);
  if (field.t) target.attr("data-type", field.t);
  if (field.vt) target.attr("data-value-type", field.vt);
  if (field.d) target.attr("data-data", field.d);
  if (field.m) target.attr("data-mode", field.m);
  if (field.u) target.attr("data-update", field.u);
  if (field.co) target.attr("data-count", field.co);
  if (field.v_0_di) target.attr("data-value-0-disabled", field.v_0_di);
  if (field.v_1_di) target.attr("data-value-1-disabled", field.v_1_di);
  if (field.cl) target.addClass(field.cl);
  if (field.ca) {
    var tmp = $("#tmp_caption").clone();
    tmp.removeAttr("id");
    tmp.find(".caption").html(field.ca);
    target.append(tmp);
  }
  if (field.vv) {
    target.attr("data-value-view", field.vv);
    target.addClass("hide");
  }
  if (field.e) { 
    field.e = val_to_bool(field.e);
  } else {
    field.e = false;
  }
}


function attr_lbl(field, target) {
  target.text(field.l);
  if (field.i) target.prepend(add_icon_inline(field.i));
  if (field.cl_lbl) target.addClass(field.cl_lbl);
}


function attr_inp(field, target) {
  if (field.cl_in) {
    target.addClass(field.cl_in);
  } else if (field.cl_c) {
    target.addClass(field.cl_c);
  }
  if (field.s) target.attr("style", field.s);
  if (field.al) target.addClass(field.al);
  if (field.ti) target.attr("tabindex", field.ti);
  if (field.af) if (val_to_bool(field.af)) target.attr("autofocus", true);
  if (field.di) if (val_to_bool(field.di)) target.attr("disabled", true);
  if (field.r) {
    if (field.v) {
      if (field.v != "") {
        target.removeClass("required");
        add_caption_r(field, target, false);
      } else {
        target.addClass("required");
        add_caption_r(field, target, true);
      }
    } else {
      target.addClass("required");
      add_caption_r(field, target, true);
    }
  }
}


function attr_inp_str(field, target) {
  if (field.min) target.attr("minlenght", field.min);
  if (field.max) target.attr("maxlenght", field.max);
  if (field.ph) target.attr("placeholder", field.ph);
  if (field.ac) target.attr("autocomplete", val_to_bool(field.ac) ? "on" : "off");
  if (field.sc) target.attr("spellcheck", val_to_bool(field.ac) ? "true" : "false");
  if (field.r) target.attr("data-required", val_to_bool(field.r) ? "true" : "false");
  if (field.pa) target.attr("data-pattern", field.pa);
}


function attr_inp_num(field, target) {
  if (field.min) target.attr("min", field.min);
  if (field.max) target.attr("max", field.max);
  if (field.step) target.attr("step", field.step);
  if (field.ph) target.attr("placeholder", field.ph);
  if (field.ac) target.attr("autocomplete", val_to_bool(field.ac) ? "on" : "off");
  if (field.r) target.attr("data-required", val_to_bool(field.r) ? "true" : "false");
  if (field.pa) target.attr("data-pattern", field.pa);
}


function attr_vs(field, value=["off=Off", "on=On"]) {
  if (field.vs) {
    field.vs = val_to_array(field.vs);
  } else {
    if (cfg["vd"][field.t]) {
      field.vs = val_to_array(cfg["vd"][field.t]);
    } else {
      field.vs = value;
    }
  }

  for (var i = 0; i < field.vs.length; i++) {
    if (!Array.isArray(field.vs[i])) {
      var v = field.vs[i].split(cfg.main.delimiter_val);
      field.vs[i] = [];
      field.vs[i][0] = v[0];
      if (v[1]) {
        field.vs[i][1] = v[1];
      } else {
        field.vs[i][1] = v[0];
      }
    }
  }
}


function attr_vs_content(content, value=null) {
  if (!value) return content;
  value = val_to_array(value);
  for (var i = 0; i < value.length; i++) {
    var v = value[i].split(cfg.main.delimiter_val);
    if (v[0] == content && v[0] && v[1]) return v[1];
  }
  return content
}


function attr_is(field) {
  if (field.is) {
    field.is = val_to_array(field.is);
  } else {
    if (cfg["id"][field.t]) field.is = val_to_array(cfg["id"][field.t]);
  }
}


function attr_msgs(field, value=["", ""]) {
  if (field.msgs) {
    field.msgs = val_to_array(field.msgs);
  } else {
    if (cfg["msgsd"][field.t]) {
      field.msgs = val_to_array(cfg["msgsd"][field.t]);
    } else {
      field.msgs = value;
    }
  }
}


function attr_val_disabled(field, val) {
  val = val_to_bool(val);

  names = field.v_0_di;
  if (names) {
    names = val_to_array(names);
    for (var i = 0; i < names.length; i++) {
      if (names[i] != "") {
        $("[data-name=" + names[i] + "]").each(function() {
          if (val) {
            $(this).find(".in").attr("disabled", false);
          } else {
            $(this).find(".in").attr("disabled", true);
          }
        });
      }
    }
  }

  names = field.v_1_di;
  if (names) {
    names = val_to_array(names);
    for (var i = 0; i < names.length; i++) {
      if (names[i] != "") {
        $("[data-name=" + names[i] + "]").each(function() {
          if (val) {
            $(this).find(".in").attr("disabled", true);
          } else {
            $(this).find(".in").attr("disabled", false);
          }
        });
      }
    }
  }
}


function attr_val_view(field, val) {
  val = val_to_bool(val);

  names = field.v_0_v;
  if (names) {
    names = val_to_array(names);
    for (var i = 0; i < names.length; i++) {
      if (names[i] != "") {
        $("[data-name=" + names[i] + "]").each(function() {
          if (val) {
            $(this).removeClass("hide");
          } else {
            $(this).addClass("hide");
          }
        });
      }
    }
  }

  names = field.v_1_v;
  if (names) {
    names = val_to_array(names);
    for (var i = 0; i < names.length; i++) {
      if (names[i] != "") {
        $("[data-name=" + names[i] + "]").each(function() {
          if (val) {
            $(this).addClass("hide");
          } else {
            $(this).removeClass("hide");
          }
        });
      }
    }
  }
  
  names = field.v_v;
  if (names) {
    names = val_to_array(names);
    for (var i = 0; i < names.length; i++) {
      if (names[i] != "") {
        $("[data-name=" + names[i] + "]").each(function() {
          if ($(this).hasClass("hide")) {
            $(this).removeClass("hide");
          } else {
            $(this).addClass("hide");
          }
        });
      }
    }
  }
}


function attr_class_switch(target, val, class_0 = "btn-default", class_1 = "btn-primary") {
  if (val_to_bool(val)) {
    if (class_1) target.addClass(class_1);
    if (class_0) target.removeClass(class_0);
  } else {
    if (class_0) target.addClass(class_0);
    if (class_1) target.removeClass(class_1);
  }
}


//update
function update(d) {
  if (error_check(d)) {
    if (d[cfg.main.json_config]) cfg_process(d[cfg.main.json_config]);
    if (d[cfg.main.json_data]) data_process(d[cfg.main.json_data]);
    if (d[cfg.main.json_config_live]) live_cfg_process(d[cfg.main.json_config_live]);
    if (d[cfg.main.json_data_live]) live_data_process(d[cfg.main.json_data_live]);
    if (d[cfg.main.json_msg] != undefined) toast_show(d[cfg.main.json_msg]);  
  }
  if (d[cfg.main.json_cmd]) cmd_execute(d[cfg.main.json_cmd]);
  if (d[cfg.main.json_toasts]) toasts_show(d[cfg.main.json_toasts]);
  if (d[cfg.main.json_uid]) spinner_update(d[cfg.main.json_uid], false);
  if (d[cfg.main.json_session]) session_process(d[cfg.main.json_session]);
}


function update_val(name, val, val_type = "remote") {
  $("[data-data=" + name + "]").each(function() {
    var type = $(this).attr("data-value-type");
    if (type) {
      if (type != val_type && type != "both") return;
    }
    update_val_data(name, val, $(this));
    update_val_all(name, val, $(this));
  });

  $("[data-name=" + name + "]").each(function() {
    var type = $(this).attr("data-value-type");
    if (type) {
      if (type != val_type && type != "both") return;
    }
    update_val_name(name, val, $(this));
    update_val_all(name, val, $(this));
    update_val_disabled(name, val, $(this));
  });

  $("[data-value-view=" + name + "]").each(function() {
    var type = $(this).attr("data-value-type");
    if (type) {
      if (type != val_type && type != "both") return;
    }
    if (val_to_bool(val) == 1) {
      $(this).removeClass("hide");
    } else {
      $(this).addClass("hide");
    }
  });
}


function update_val_data(name, val, group) {
  var type = group.attr("data-type");
  var data = group.attr("data-data");
  var mode = group.attr("data-mode");
  var update = group.attr("data-update");
  var ready = group.attr("data-ready");
  var count = group.attr("data-count");
  if (!count) count = 0;
  if (!update && ready) return;

  if (type == "select" || type == "selectbutton" || type == "selectlist") {
    group.attr("data-ready", true);
    var inp = group.find(".in");
    inp.html("");
    val = val_to_array(val);
    for (var i = 0; i < val.length; i++) {
      var v = val[i].split(cfg.main.delimiter_val);;
      var option = $("#tmp_select_option").clone();
      option.removeAttr("id");
      if (v[1]) {
        option.attr("value", v[0]);
        v[0] = v[1];
      } else if (mode == "string") {
        option.attr("value", v[0]);
      } else {
        option.attr("value", i);
      }
      option.text(v[0]);
     inp.append(option);
    }
  } else if (type == "radio") {
    var inp = group.find(".in");
    inp.html("");
    val = val_to_array(val);
    for (var i = 0; i < val.length; i++) {
      var v = val[i].split(cfg.main.delimiter_val);
      var option = $("#tmp_radio_input").clone();
      option.attr("id", name + "-" + i);
      option.attr("name", name);
      if (v[1]) {
        option.attr("value", v[0]);
        v[0] = v[1];
      } else if (mode == "string") {
        option.attr("value", v[0]);
      } else {
        option.attr("value", i);
      }
      var lbl = $("#tmp_radio_label").clone();
      lbl.removeAttr("id");
      lbl.attr("for", name + "-" + i);
      lbl.text(v[0]);
      var span = $("#tmp_radio_checkmark").clone();
      span.removeAttr("id");
      lbl.append(option);
      lbl.append(span);
      inp.append(lbl);
    }
  } else if (type == "radiogroup") {
    var inp = group.find(".in");
    inp.html("");
    val = val_to_array(val);
    for (var i = 0; i < val.length; i++) {
      var v = val[i].split(cfg.main.delimiter_val);
      var option = $("#tmp_radiogroup_input").clone();
      option.attr("id", name + "-" + i);
      option.attr("name", name);
      if (v[1]) {
        option.attr("value", v[0]);
        v[0] = v[1];
      } else if (mode == "string") {
        option.attr("value", v[0]);
      } else {
        option.attr("value", i);
      }
      var lbl = $("#tmp_radiogroup_label").clone();
      lbl.removeAttr("id");
      lbl.attr("for", name + "-" + i);
      lbl.text(v[0]);
      inp.append(option);
      inp.append(lbl);
    }
  } else if (type == "buttongroup") {
    var inp = group.find(".in");
    inp.html("");
    val = val_to_array(val);
     for (var i = 0; i < val.length; i++) {
       var v = val[i].split(cfg.main.delimiter_val);
       var option = $("#tmp_buttongroup_button").clone();
       if (v[1]) {
         option.attr("value", v[0]);
         v[0] = v[1];
       } else if (mode == "string") {
         option.attr("value", v[0]);
       } else {
         option.attr("value", i);
       }
       option.html(v[0]);
       option.click(function() {
         send_val(group, inp.value);
       });
       inp.append(option);
    }
  }
}


function update_val_name(name, val, group) {
  var type = group.attr("data-type");
  var data = group.attr("data-data");
  var values = group.attr("data-values");
  var mode = group.attr("data-mode");
  var update = group.attr("data-update");
  var ready = group.attr("data-ready");
  var count = group.attr("data-count");
  if (!count) count = 0;

  if (type == "date" || type == "editor" || type == "editor_code" || type == "email" || type == "hidden" || type == "month" || type == "number" || type == "numberslider" || type == "password" || type == "search" || type == "select" || type == "selectbutton" || type == "selectlist" || type == "slider" || type == "tel" || type == "text"  || type == "textbutton" || type == "textarea" || type == "time" || type == "url" || type == "week") {
    group.find(".in").val(val);
  } else if (type == "passwordverify") {
    group.find(".in-1").val(val);
    group.find(".in-2").val(val);
  } else if (type == "checkbox" || type == "checkboxslider") {
    if (group.attr("data-values")) {
      if (val.toLowerCase() == val_to_array(group.attr("data-values"))[1].toLowerCase()) {
        group.find(".in").prop("checked", true);
      } else {
        group.find(".in").prop("checked", false);
      }
    } else {
      if (val_to_bool(val) == 1) {
        group.find(".in").prop("checked", true);
      } else {
        group.find(".in").prop("checked", false);
      }
    }
  } else if (type == "radio" || type == "radiogroup") {
    var inp = group.find(".in");
    $("input", inp).each(function() {
      if ($(this).val() == val) {
        $(this).prop("checked", true);
      } else {
        $(this).prop("checked", false);
      }
    });
  } else if (type == "status") {
    var inp = group.find(".in");
    $("span", inp).each(function() {
      if ($(this).attr("data-value") == val) {
        $(this).addClass("active");
      } else {
        $(this).removeClass("active");
      }
    });
  } else if (type == "color") {
    group.find(".in").val("#" + val);
  } else if (type == "colorpicker") {
    if (val == "000000") val = "FFFFFF"
    try {
      input_colorpicker.color.set("#" + val);
    } catch (e) {
      input_colorpicker.color.set("#FFFFFF");
    }
  } else if (type == "colorslider") {
    var inp_r = group.find(".in-r");
    var inp_g = group.find(".in-g");
    var inp_b = group.find(".in-b");
    var comp = val_hex_to_rgb_comp(val);
    inp_r.val(comp.r);
    inp_g.val(comp.g);
    inp_b.val(comp.b);
  } else if (type == "toggle") {
    val = val_to_bool(val);
    var inp = group.find(".in");
    if (inp.length) {
      inp.val(val);
      attr_class_switch(inp, val);
    } else {
      var cls = val ? "m-item active" : "m-item";
      if (val) {
        if (group.attr("data-class-1")) cls = cls + " " + group.attr("data-class-1");
        if (group.attr("data-style-1")) group.attr("style", group.attr("data-style-1"));
      } else {
        if (group.attr("data-class-0")) cls = cls + " " + group.attr("data-class-0");
        if (group.attr("data-style-0")) group.attr("style", group.attr("data-style-0"));
      }
      group.attr("class", cls);
      group.attr("data-value", val);
      group.find("a").attr("data-value", val);
    }
  } else if (type == "switch") {
    attr_class_switch(group.find(".btn-on"), val);
    attr_class_switch(group.find(".btn-off"), val, "btn-primary", "btn-default");
  } else if (type == "show" || type == "view") {
    val = val_to_bool(val);
    if (val) group.removeClass("hide");
    if (!val) group.addClass("hide");
  } else if (type == "table") {
    var inp = group.find("tbody");
    inp.empty();
    if (mode == "string") {
       if (typeof(val) == "string") inp.append(val);
    } else if (mode == "array") {
      if (typeof(val) != "object") { if (val != "") { val = jQuery.parseJSON(val); } }
      if (typeof(val) == "object") {
        jQuery.each(val, function(i, v) {
          if (typeof(v) == "object") {
            jQuery.each(v, function(i, v) {
              var str = "";
              jQuery.each(v, function(i, v) { if (i < count) str += "<td>" + v + "</td>"; });
              inp.append("<tr>" + str + "</tr>");
            });
          }
        });
      }
    } else {
      if (typeof(val) == "string") {
        inp.append(val)
      } else {
        jQuery.each(val, function(i, v) {
          if (typeof(v) == "object") {
            inp.append("<tr><th colspan='2'>" + i + "</th></tr>");
            jQuery.each(v, function(i, v) {
              inp.append("<tr><td>" + i + "</td><td>" + v + "</td></tr>");
            });
          } else {
            inp.append("<tr><td>" + i + "</td><td>" + v + "</td></tr>");
          }
        });
      }
    }
  }
}


function update_val_all(name, val, group) {
  var type = group.attr("data-type");
  var data = group.attr("data-data");
  var values = group.attr("data-values");
  var max = group.attr("data-max");
  var mode = group.attr("data-mode");
  var update = group.attr("data-update");
  var ready = group.attr("data-ready");
  var count = group.attr("data-count");
  if (!count) count = 0;

  if (type == "class") {
    group.attr("class", val);
  } else if (type == "html") {
    if (values) val = attr_vs_content(val, values);
    if (val == "") {
      group.html(val);
      return;
    }
    val = val.replace(/\n/g, "<br>");
    if (mode == "prepend") {
      val = val + group.html();
      if (max) if (val.length > max) val = val.slice(max);
      group.html(val);
    } else if (mode == "append") {
      val = group.html() + val;
      if (max) if (val.length > max) val = val.slice(max);
      group.html(val);
    } else {
      if (max) if (val.length > max) val = val.slice(max);
      group.html(val);
    }
  } else if (type == "icon") {
    if (values) val = attr_vs_content(val, values);
    var inp = group.find(".in");
    if (inp.length) {
      inp.html(add_icon_inline(val));
    } else {
      group.html(add_icon_inline(val));
    }
  } else if (type == "image") {
    if (values) val = attr_vs_content(val, values);
    if (val.indexOf("http") !== -1 || val.startsWith(cfg.main.url_images) || val.startsWith("../")) {
      group.find(".in").attr("src", val);
    } else {
      group.find(".in").attr("src", cfg.main.url_images + val);
    }
  } else if (type == "id") {
    group.attr("id", val);
  } else if (type == "label") {
    if (values) val = attr_vs_content(val, values);
    if (val == "") {
      group.find(".lbl").text(val);
      return;
    }
    if (mode == "prepend") {
      val = val + group.find(".lbl").text();
      if (max) if (val.length > max) val = val.slice(max);
      group.find(".lbl").text(val);
    } else if (mode == "append") {
      val = group.find(".lbl").text() + val;
      if (max) if (val.length > max) val = val.slice(max);
      group.find(".lbl").text(val);
    } else {
      if (max) if (val.length > max) val = val.slice(max);
      group.find(".lbl").text(val);
    }
  } else if (type == "progress") {
    if (values) val = attr_vs_content(val, values);
    if (val == "") val = "0";
    var inp = group.find(".in");
    inp.attr("style", "width:" + val + "%");
    inp.html(val + "%");
  } else if (type == "txt") {
    if (values) val = attr_vs_content(val, values);
    if (max) if (val.length > max) val = val.slice(max);
    if (val == "") {
      group.find(".in").html(val);
      return;
    }
    val = val.replace(/\n/g, "<br>");
    if (mode == "prepend") {
      val = val + group.find(".in").html();
      if (max) if (val.length > max) val = val.slice(max);
      group.find(".in").html(val);
    } else if (mode == "append") {
      val = group.find(".in").html() + val;
      if (max) if (val.length > max) val = val.slice(max);
      group.find(".in").html(val);
    } else {
      if (max) if (val.length > max) val = val.slice(max);
      group.find(".in").html(val);
    }
  }
}


function update_val_disabled(name, val, group) {
  val = val_to_bool(val);
  var names;

  names = group.attr("data-value-0-disabled");
  if (names) {
    names = val_to_array(names);
    for (var i = 0; i < names.length; i++) {
      if (names[i] != "") {
        $("[data-name=" + names[i] + "]").each(function() {
          if (val) {
            $(this).find(".in").attr("disabled", false);
          } else {
            $(this).find(".in").attr("disabled", true);
          }
        });
      }
    }
  }

  names = group.attr("data-value-1-disabled");
  if (names) {
    names = val_to_array(names);
    for (var i = 0; i < names.length; i++) {
      if (names[i] != "") {
        $("[data-name=" + names[i] + "]").each(function() {
          if (val) {
            $(this).find(".in").attr("disabled", true);
          } else {
            $(this).find(".in").attr("disabled", false);
          }
        });
      }
    }
  }
}


function update_val_live_leds(d) {
  var str = "linear-gradient(90deg,";
  $.each(d, function(key, val) {
    if (val.length > 6) val = val.substring(2);
    str += "#" + val + ",";
  });
  str = str.slice(0, -1); 
  str += ")";
  $(".live_leds").css("background", str);
}


//data
function data_get(val) {
  var uid_current = uid();
  spinner_update(uid_current);

  var json = {};
  json[cfg.main.json_uid] = uid_current;
  json[cfg.main.json_version] = cfg.main.version;
  json[cfg.main.json_lng] = cfg.main.lng;
  json[cfg.main.json_cmd] = cfg.main.json_val_get;
  val = val_to_array(val);
  json[cfg.main.json_data] = val;

  if (cfg_local.con_type) {
    ws.send(JSON.stringify(json));
  } else {
    var ajax_headers = {};
    var ajax_data = ""
    var json_str = JSON.stringify(json);
    if (cfg_local.url_web.length + json_str.length >= cfg.main.get_size_url) {
      if (json_str.length <= cfg.main.get_size_header) ajax_headers[cfg.main.json] = json_str;
    } else {
      ajax_data = cfg.main.json + '=' + json_str;
    }
    $.ajax({
      type: 'GET',
      url: cfg_local.url_web,
      timeout: cfg.main.get_timeout*1000,
      headers: ajax_headers,
      data: ajax_data,
      dataType: 'json',
      cache: false,
      success: function(d) {
        update(d);
      }, error: function(d) {
        toast_show(cfg.main.msg_error_con, true);
      }
    });
  }
}


function data_set(val) {
  var json = {};
  if (cfg.main.json_data_send != "") json[cfg.main.json_data_send] = {};
  val = val_to_array(val);
  for (var i = 0; i < val.length; i++) {
    var d = val[i].split("=");
    if (d[1]) {
      if (cfg.main.json_data_send != "") {
        json[cfg.main.json_data_send][d[0]] = d[1];
      } else {
        json[d[0]] = d[1];
      }
    }
  }
  send(json);
}


//set
function set_field_toggle(target) {
  var body = target.find(".body");
  if (body.hasClass("hide")) {
    target.find(".header").addClass("active");
    body.removeClass("hide");
    return true;
  } else {
    target.find(".header").removeClass("active");
    body.addClass("hide");
    return false;
  }
}


function set_fieldgroup_toggle(target) {
  if (cfg.main.save_view) {
    if (!cfg_local["group"]) cfg_local["group"] = {};
    cfg_local["group"][target.attr("data-group")] = target.attr("data-group-index");
    cfg_local_save();
  }

  $("[data-group=" + target.attr("data-group") + "]").each(function() {
    if ($(this).attr("data-group-index") == target.attr("data-group-index")) {
      $(this).find(".header").addClass("inactive");
      $(this).find(".body").removeClass("hide");
    } else {
      $(this).find(".header").removeClass("inactive");
      $(this).find(".body").addClass("hide");
    }
  });
}


function set_group_toggle(target) {
  var body = target.find(".bodys");
  if (body.hasClass("hide")) {
    target.find(".header_container").addClass("active");
    body.removeClass("hide");
  } else {
    target.find(".header_container").removeClass("active");
    body.addClass("hide");
  }
}


function set_tabgroup_toggle(target) {
  $("[data-group=" + target.attr("data-group") + "]").each(function() {
    if ($(this).attr("data-group-index") == target.attr("data-group-index")) {
      $(this).addClass("active");
    } else {
      $(this).removeClass("active");
    }
  });
}


function set_tabgroup_container_toggle(target) {
  var body = target.find(".bodys");
  if (body.hasClass("hide")) {
    target.find(".header_container").addClass("active");
    target.find(".nav").removeClass("hide");
    body.removeClass("hide");
  } else {
    target.find(".header_container").removeClass("active");
    target.find(".nav").addClass("hide");
    body.addClass("hide");
  }
}


function set_toggle_val(field, val) {
  val ^= 1;
  update_val(field.n, val);
  send_val(field, val ? field.vs[1][0] : field.vs[0][0]);
}


function set_switch_val(field, btn_on, btn_off, val) {
  attr_class_switch(btn_on, val);
  attr_class_switch(btn_off, val, "btn-primary", "btn-default");
  send_val(field, val ? field.vs[1][0] : field.vs[0][0]);
}


//send
function send_local(json) {
  if (cfg.main.save_data) {
    if (!cfg_local["data"]) cfg_local["data"] = {};
    $.each(json[cfg.main.json_data_send], function(key, val) {
      cfg_local["data"][key] = val;
    });
    cfg_local_save();
  }
}


function send(json, field = undefined) {
  var uid_current = uid();

  json[cfg.main.json_uid] = uid_current;
  json[cfg.main.json_version] = cfg.main.version;
  json[cfg.main.json_lng] = cfg.main.lng;
  json[cfg.main.json_cmd] = cfg.main.json_val_set;

  if (field.m == "download") {
    const lnk = document.createElement("a");
    lnk.href = cfg_local.url_web + "?file=''&json="+JSON.stringify(json);
    lnk.download = "";
    document.body.appendChild(lnk);
    lnk.click();
    document.body.removeChild(lnk);
    return;
  }

  spinner_update(uid_current);
  if (cfg_local.con_type) {
    ws.send(JSON.stringify(json));
  } else {
    $.ajax({
      type: 'POST',
      url: cfg_local.url_web,
      timeout: cfg.main.post_timeout*1000,
      data: cfg.main.json + '=' + JSON.stringify(json),
      dataType: 'json',
      cache: false,
      success: function(d) {
        update(d);
        if (field.cmd_s) cmd_execute(field.cmd_s);
      }, error: function(d) {
        if (!field.e) toast_show(cfg.main.msg_error_con, true);
        if (field.cmd_e) cmd_execute(field.cmd_e);
      }
    });
  }
}


function send_val(field, val) {
  val = val_array_to_val(val);

  if (field.v_0_di || field.v_1_di) attr_val_disabled(field, val);
  if (field.v_0_v || field.v_1_v || field.v_v) attr_val_view(field, val);

  if (field.submit && field.submit != "" && !field.tx) {
    if (!data["data_send"][field.submit]) data["data_send"][field.submit] = {};
    data["data_send"][field.submit][field.n] = val;
    if (field.cmd) cmd_execute(field.cmd);
    if (field.get) data_get(field.get);
    if (field.set) data_get(field.set);
    return;
  }

  var json = {};
  if (cfg.main.json_data_send != "") {
    json[cfg.main.json_data_send] = {};
    json[cfg.main.json_data_send][field.n] = val;
  } else {
    json[field.n] = val;
  }

  if (field.vt) {
    if (field.vt == "local" || field.vt == "both") send_local(json);
    if (field.vt == "remote" || field.vt == "both") send(json, field);
  } else {
    send(json, field);
  }

  if (field.cmd) cmd_execute(field.cmd);
  if (field.get) data_get(field.get);
  if (field.set) data_get(field.set);
}


function send_val_delay(field, val, target) {
  val = val_array_to_val(val);

  if (field.v_0_di || field.v_1_di) attr_val_disabled(field, val);
  if (field.v_0_v || field.v_1_v || field.v_v) attr_val_view(field, val);

  var valid = true;

  if (field.r) {
    if (val != "") {
      if (target) {
        target.removeClass("required");
        add_caption_r(field, target, false);
      }
    } else {
      if (target) {
        target.addClass("required");
        add_caption_r(field, target, true);
      }
      valid = false;
    }
  }

  if (field.pa) {
    if (val == "" || val.match(field.pa)) {
      if (target && valid) {
        target.removeClass("invalid");
        add_caption_pa(field, target, false);
      }
    } else {
      if (target) {
        target.addClass("invalid");
        add_caption_pa(field, target, true);
      }
      valid = false;
    }
  }

  if (field.submit && field.submit != "" && !field.tx) {
    if (!data["data_send"][field.submit]) data["data_send"][field.submit] = {};
    if (valid) {
      data["data_send"][field.submit][field.n] = val;
    } else {
      delete data["data_send"][field.submit][field.n];
    }
    valid = false;
  }

  clearTimeout(send_val_timer);
  if (valid) send_val_timer = setTimeout(function() { send_val(field, val); }, 300);

  if (field.cmd) cmd_execute(field.cmd);
}


function send_val_submit(field, val) {
  if (field.submit == "") return;
  if (!data["data_send"][field.submit]) data["data_send"][field.submit] = {};

  if (!cfg.main.submit_empty && !field.txe) {
    if (Object.keys(data["data_send"][field.submit]).length == 0) {
      toast_show(cfg.main.msg_error_empty, true);
      return;
    }
  }

  val = val_array_to_val(val);

  if (field.v_0_di || field.v_1_di) attr_val_disabled(field, val);
  if (field.v_0_v || field.v_1_v || field.v_v) attr_val_view(field, val);

  var json = {};
  if (cfg.main.json_data_send != "") {
    json[cfg.main.json_data_send] = JSON.parse(JSON.stringify(data["data_send"][field.submit]));
    json[cfg.main.json_data_send][field.n] = val;
  } else {
    json = JSON.parse(JSON.stringify(data["data_send"][field.submit]));
    json[field.n] = val;
  }

  if (field.vt) {
    if (field.vt == "local" || field.vt == "both") send_local(json);
    if (field.vt == "remote" || field.vt == "both") send(json, field);
  } else {
    send(json, field);
  }

  if (field.cmd) cmd_execute(field.cmd);
  if (field.get) data_get(field.get);
  if (field.set) data_get(field.set);
}


function send_val_abort(field, val) {
  if (field.submit == "") return;
  if (data["data_send"][field.submit]) delete data["data_send"][field.submit];

  val = val_array_to_val(val);

  if (field.v_0_di || field.v_1_di) attr_val_disabled(field, val);
  if (field.v_0_v || field.v_1_v || field.v_v) attr_val_view(field, val);

  if (field.cmd) cmd_execute(field.cmd);
  if (field.get) data_get(field.get);
  if (field.set) data_get(field.set);
}


function send_upload(field, target) {
  var val = target[0].files[0].name;
  var valid = true;

  if (field.r) {
    if (val != "") {
      if (target) {
        target.removeClass("required");
        add_caption_r(field, target, false);
      }
    } else {
      if (target) {
        target.addClass("required");
        add_caption_r(field, target, true);
      }
      valid = false;
    }
  }

  if (field.pa) {
    if (val == "" || val.match(field.pa)) {
      if (target && valid) {
        target.removeClass("invalid");
        add_caption_pa(field, target, false);
      }
    } else {
      if (target) {
        target.addClass("invalid");
        add_caption_pa(field, target, true);
      }
      valid = false;
    }
  }

  if (field.max) {
    if (target[0].files[0].size <= field.max) {
      if (target && valid) target.removeClass("invalid");
    } else {
       if (target) target.addClass("invalid");
       valid = false;
    }
  }

  if (valid) {
    var data = new FormData();
    data.append('file', target[0].files[0]);

    var uid_current = uid();
    spinner_update(uid_current);

    json = {}
    json[cfg.main.json_uid] = uid_current;
    json[cfg.main.json_version] = cfg.main.version;
    json[cfg.main.json_lng] = cfg.main.lng;
    json[cfg.main.json_cmd] = cfg.main.json_val_upload;
    json[cfg.main.json_data_send] = {};
    json[cfg.main.json_data_send][field.n] = val
    data.append(cfg.main.json, JSON.stringify(json));

    $.ajax({
      type: 'POST',
      url: cfg_local.url_web,
      timeout: cfg.main.post_upload_timeout*1000,
      data: data,
      processData: false,
      contentType: false,
      cache: false,
      success: function(d) {
        d = jQuery.parseJSON(d);
        update(d);
        spinner_update(uid_current, false)
      }, error: function(d) {
        spinner_update(uid_current, false)
        toast_show(cfg.main.msg_error_upload, true);
      }
    });
  }
}


//cmd
function cmd_execute(cmds) {
  cmds = cmds.split(cfg.main.delimiter_1);
  $.each(cmds, function(i, cmd) {
    if (cmd == "reconnect") {
      live_check(false);
      show(false);
      menu_show(false);
      popup_close();
      toast_show(cfg.main.msg_reconnect, false, 0);
      ws_close();
      setTimeout(function() { setup("user"); }, cfg.main.reload_delay*1000);
    } else if (cmd == "reload") {
      setup("user");
    } else if (cmd == "load config" || cmd == "reload config") {
      cfg_data_load(true, false, "user");
    } else if (cmd == "load data" || cmd == "reload data") {
      cfg_data_load(false, true, "user");
    } else if (cmd == "mode screen") {
      mode_screen();
    } else if (cmd == "popup close") {
      popup_close();
    } else if (cmd == "menu close") {
      menu_close();
    } else if (cmd == "menu hide") {
      menu_show(false);
    } else if (cmd == "menu view") {
      menu_show(true);
    } else if (cmd == "content hide") {
      show(false);
    } else if (cmd == "content view") {
      show(true);
    } else if (cmd == "hide") {
      show(false);
      menu_show(false);
    } else if (cmd == "view") {
      show(true);
      menu_show(true);
    } else if (cmd == "close" || cmd == "exit") {
      window.close();
    } else if (cmd == "reset" || cmd == "reset browser" || cmd == "reload browser") {
      window.onbeforeunload = null;
      window.location.reload();
    } else if (cmd == "tab_prev") {
      tab_switch(1);
    } else if (cmd == "tab_next") {
      tab_switch(-1);
    } else if (cmd == "tab_first") {
      tab_show(0);
    } else if (cmd == "tab_last") {
      tab_show(255);
    } else if (cmd == "toast" || cmd == "msg" || cmd == "message") {
      toast_show("");
    } else {
      var [key, val] = [cmd.slice(0, cmd.indexOf(' ')), cmd.slice(cmd.indexOf(' ') + 1)];
      if (key == "page") {
        page_show(val);
      } else if (key == "tab") {
        tab_show(val);
      } else if (key == "popup") {
        popup_show(val);
      } else if (key == "show" || key == "view" || key == "open") {
        val = val.split("\\");
        if (val[0]) page_show(val[0]);
        if (val[1]) tab_show(val[1]);
      } else if (key == "toast" || key == "msg" || key == "message") {
        toast_show(val);
      } else if (key == "toasts") {
        toasts_show(val);
      } else if (key == "get") {
        data_get(val);
      } else if (key == "set" || key == "post") {
        data_set(val);
      }
    }
  });
}


//value convert
function val_to_bool(val) {
  if (val == "on" || val == "On" || val == "true" || val == "True" || val == "yes" || val == "Yes" || val == "1" || val == "open" || val == "opened" || val == "up") {
    val = 1;
  } else if (val == "off" || val == "Off" || val == "false" || val == "False" || val == "no" || val == "No" || val == "0" || val == "close" || val == "closed" || val == "down") {
    val = 0;
  } else if (val != "") {
    val = 1;
  } else if (val == "") {
    val = 0;
  }
  return val;
}


function val_int_to_hex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}


function val_rgb_to_hex(rgb) {
  rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
  return val_int_to_hex(parseInt(rgb[1])) + val_int_to_hex(parseInt(rgb[2])) + val_int_to_hex(parseInt(rgb[3]));
}


function val_rgb_comp_to_hex(r, g, b) {
  return val_int_to_hex(parseInt(r)) + val_int_to_hex(parseInt(g)) + val_int_to_hex(parseInt(b));
}


function val_hex_to_rgb_comp(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}


function val_to_array(val, fallback = true, def = []) {
  if (!Array.isArray(val)) {
    if (val == "") return def;
    if (fallback) {
      if (val.indexOf(cfg.main.delimiter_1) !== -1) {
        val = val.split(cfg.main.delimiter_1);
      } else if (val.indexOf(cfg.main.delimiter_2) !== -1) {
        val = val.split(cfg.main.delimiter_2);
      } else {
        val = val.split(cfg.main.delimiter_1);
      }
    }
    else {
      val = val.split(cfg.main.delimiter_1);
    }
  }
  return val;
}


function val_array_to_val(val) {
  if (Array.isArray(val)) val = val.join(cfg.main.delimiter_1);
  return val;
}


//live
function live_cfg_process(d) {
  submit = "";
  if (cfg.main.submit_global) {
    $.each(d, function(key, val) {
      $.each(val, function(i, field) {
        if (field.t == "submit" || field.t == "submit_confirm") submit = uid();
      });
    });
  }

  $.each(d, function(key, val) {
    $("[data-name=" + key + "]").removeClass("hide");
    $("[data-name=" + key + "]").html("");
    $.each(val, function(i, field) {
      if ((field.t == "submit" || field.t == "submit_confirm") && submit == "") submit = uid();
    });
    add_content(val, $("[data-name=" + key + "]"), submit);
  });

  var page = $(".active[data-type=page]");
  var tab = page.find(".active[data-type=tab]");
  tab.find("[autofocus=autofocus]").first().focus();
}


function live_data_process(d) {
  $.each(d, function(key, val) {
    update_val(key, val);
  });
}


var live_timer;
function live_check(val = true) {
  clearTimeout(live_timer);
  if (val) {
    var array = [];
    var page = $(".active[data-type=page]");
    var tab = page.find(".active[data-type=tab]");
    tab.find("[data-type=live]").each(function() {
      array.push($(this).attr("data-name"));
    });
    if (array.length > 0) live_timer = setTimeout(function() { live_get(array); }, 2000);
  }
}


function live_get(array) {
  var json = {};
  json[cfg.main.json_uid] = uid();
  json[cfg.main.json_version] = cfg.main.version;
  json[cfg.main.json_lng] = cfg.main.lng;
  json[cfg.main.json_cmd] = cfg.main.json_val_live_cfg_data;
  json[cfg.main.json_data_live] = array;

  if (cfg_local.con_type) {
    ws.send(JSON.stringify(json));
  } else {
    var ajax_headers = {};
    var ajax_data = ""
    var json_str = JSON.stringify(json);
    if (cfg_local.url_web.length + json_str.length >= cfg.main.get_size_url) {
      if (json_str.length <= cfg.main.get_size_header) ajax_headers[cfg.main.json] = json_str;
    } else {
      ajax_data = cfg.main.json + '=' + json_str;
    }
    $.ajax({
      type: 'GET',
      url: cfg_local.url_web,
      timeout: cfg.main.get_timeout*1000,
      headers: ajax_headers,
      data: ajax_data,
      dataType: 'json',
      cache: false,
      success: function(d) {
        update(d);
        live_timer = setTimeout(function() { live_get(array); }, 2000);
      }, error: function(d) {
        live_timer = setTimeout(function() { live_get(array); }, 2000);
      }
    });
  }
}


//ui - menu
function menu_show(val = true) {
  if (val) {
    $("#menu").removeClass("hide");
  } else {
    $("#menu").addClass("hide");
  }
}


function menu_close() {
  $("#menu").scrollTop(0);
  $("#m-cb").prop("checked", false);
}


function menu_toggle() {
  if ($("#m-cb").is(":checked")) {
    $("#m-cb").prop("checked", false);
  } else {
      $("#m-cb").prop("checked", true);
  }
}


function menu_switch(i, pos) {
  if (i == -1 && pos < cfg.main.slide_menu_area_size && $("#m-cb").is(":checked")) {
    menu_toggle();
  } else if (i == 1 && pos < cfg.main.slide_menu_area_size && !$("#m-cb").is(":checked")) {
    menu_toggle();
  } else if (i == -1 && pos < cfg.main.slide_menu_area_size && cfg.main.slide_menu_up) {
    menu_toggle();
  }
}


//ui - page
function page_show(i) {
  if (isNaN(parseInt(i))) {
    i = $("[data-page_name='" + i + "']").attr("data-page");
    if (!i) return;
  }

  if (cfg.main.save_view) {
    cfg_local["page"] = i;
    cfg_local_save();
  }

  if (cfg.main.scroll_page) window.scrollTo({top:0});
  page_show_set(i);

  if ($("[data-page=" + i + "]").attr("data-get")) data_get($("[data-page=" + i + "]").attr("data-get"));
  if ($("[data-page=" + i + "]").attr("data-set")) data_set($("[data-page=" + i + "]").attr("data-set"));
  if ($("[data-page=" + i + "]").attr("data-cmd")) cmd_execute($("[data-page=" + i + "]").attr("data-cmd"));

  var page = $("[data-page=" + i + "]")
  i = page.find(".active[data-type=tabs]").attr("data-tabs");
  if (page.find("[data-tab=" + i + "]").attr("data-get")) data_get(page.find("[data-tab=" + i + "]").attr("data-get"));
  if (page.find("[data-tab=" + i + "]").attr("data-set")) data_set(page.find("[data-tab=" + i + "]").attr("data-set"));
  if (page.find("[data-tab=" + i + "]").attr("data-cmd")) cmd_execute(page.find("[data-tab=" + i + "]").attr("data-cmd"));
}


function page_show_set(i) {
  if (!cfg.c[i]) return;

  $("[data-type=page]").each(function() {
    $(this).removeClass("active");
  });
  $("[data-type=pages]").each(function() {
    $(this).removeClass("active");
    if ($(this).attr("data-class-1")) $(this).removeClass($(this).attr("data-class-1"));
    if ($(this).attr("data-class-0")) $(this).addClass($(this).attr("data-class-0"));
  });
  $("[data-page=" + i + "]").addClass("active");
  $("[data-pages=" + i + "]").addClass("active");
  if ($("[data-pages=" + i + "]").attr("data-class-1")) $("[data-pages=" + i + "]").addClass($("[data-pages=" + i + "]").attr("data-class-1"));

  if (cfg.c[i].w) document.title = cfg.c[i].w;
  if (cfg.c[i].h) $("#header").html(cfg.c[i].h);

  live_check();
}


//ui - tab
function tab_show(i) {
  var page = $(".active[data-type=page]");

  if (isNaN(parseInt(i))) {
    i = page.find("[data-tab_name='" + i + "']").attr("data-tab");
    if (!i) return;
  }

  var i_max = -1;
  page.find("[data-type=tabs]").each(function() { i_max++; });
  if (i > i_max) i = i_max;
  if (i < 0) i = 0;

  if (cfg.main.save_view) {
    if (!cfg_local["tab"]) cfg_local["tab"] = {};
    cfg_local["tab"][page.attr("data-page")] = i;
    cfg_local_save();
  }

  if (cfg.main.scroll_tab) window.scrollTo({top:0});
  tab_show_set(i, page);

  if (page.find("[data-tab=" + i + "]").attr("data-get")) data_get(page.find("[data-tab=" + i + "]").attr("data-get"));
  if (page.find("[data-tab=" + i + "]").attr("data-set")) data_set(page.find("[data-tab=" + i + "]").attr("data-set"));
  if (page.find("[data-tab=" + i + "]").attr("data-cmd")) cmd_execute(page.find("[data-tab=" + i + "]").attr("data-cmd"));
}


function tab_show_set(i, page) {
  if (!page.find("[data-tab=" + i + "]").attr("data-type")) return;
  page.find("[data-type=tab]").each(function() {
    $(this).removeClass("active");
  });
  page.find("[data-type=tabs]").each(function() {
    $(this).removeClass("active");
    if ($(this).attr("data-class-1")) $(this).removeClass($(this).attr("data-class-1"));
    if ($(this).attr("data-class-0")) $(this).addClass($(this).attr("data-class-0"));
  });
  page.find("[data-tab=" + i + "]").addClass("active");
  page.find("[data-tabs=" + i + "]").addClass("active");
  if (page.find("[data-tabs=" + i + "]").attr("data-class-1")) page.find("[data-tabs=" + i + "]").addClass(page.find("[data-tabs=" + i + "]").attr("data-class-1"));

  live_check();
}


function tab_switch(i, pos=0) {
  var page = $(".active[data-type=page]");
  var i_active = page.find(".active[data-type=tabs]").attr("data-tabs");
  var i_max = -1;
  page.find("[data-type=tabs]").each(function() { i_max++; });
  if (i == -1 && i_active < i_max) {
    tab_show(++i_active);
  } else if (i == 1 && i_active > 0) {
    tab_show(--i_active);
  }
}


//ui - slide
function slide_show(field, target, i) {
  target.find(".slide").each(function(key, obj) {
    $(obj).removeClass("active");
    if (key == i) $(obj).addClass("active");
  });

  target.find(".slide_status").each(function(key, obj) {
    $(obj).removeClass("active");
    if (key == i) $(obj).addClass("active");
  });
}


function slide_switch(field, target, i) {
  var i_active = 0;
  var i_max = -1;
  target.find(".slide").each(function() {
    i_max++;
    if ($(this).hasClass("active")) i_active = i_max;
  });

  if (i == -1 && i_active > 0) {
    slide_show(field, target, --i_active);
  } else if (i == 1 && i_active < i_max) {
    slide_show(field, target, ++i_active);
  } else if (i == -1 && i_active == 0) {
    slide_show(field, target, i_max);
  } else if (i == 1 && i_active == i_max) {
    slide_show(field, target, 0);
  }
}


//ui - wizard
function wizard_show(field, target, i) {
  var i_max = target.find(".wizard").length - 1;

  if (i == 0) {
    target.find(".btn-prev").addClass("hide");
  } else {
    target.find(".btn-prev").removeClass("hide");
  }

  if (i == i_max) {
    target.find(".btn-next").addClass("hide");
    target.find(".btn-submit").removeClass("hide");
  } else if (i > i_max) {
    target.find(".btn-next").addClass("hide");
    target.find(".btn-submit").addClass("hide");
  } else {
    target.find(".btn-next").removeClass("hide");
    target.find(".btn-submit").addClass("hide");
  }

  wizard_status(field, target, i);

  if (i <= i_max) {
    target.find(".wizard").each(function(key, obj) {
      $(obj).removeClass("active");
      if (key == i) $(obj).addClass("active");
    });
  }
}


function wizard_switch(field, target, i) {
  var i_active = 0;
  var i_max = -1;
  var valid = true;
  target.find(".wizard").each(function() {
    i_max++;
    if ($(this).hasClass("active")) {
      i_active = i_max;
      valid = wizard_validate($(this));
    }
  });

  if (i == -1 && i_active > 0) {
    wizard_show(field, target, --i_active);
  } else if (i == 1 && i_active < i_max && valid) {
    wizard_show(field, target, ++i_active);
  } else if (i == 1 && i_active == i_max && valid) {
    wizard_show(field, target, ++i_max);
    if (field.v) {
      send_val_submit(field, field.v);
    } else {
      send_val_submit(field, "");
    }
  }
}


function wizard_status(field, target, i) {
  target.find(".wizard_status").each(function(key, obj) {
    $(obj).removeClass("active");
    $(obj).removeClass("finish");
    if (key < i) {
      $(obj).addClass("finish");
    } else if (key == i) {
      $(obj).addClass("active");
    }
  });
}


function wizard_validate(wizard) {
  if (wizard.find(".invalid").length > 0 || wizard.find(".required").length > 0) {
    return false;
  } else {
    wizard.find(':input').each(function(){
      var val = $(this).val();
      if ($(this).attr("data-required")) if ($(this).attr("data-required") == "true" && val == "") return false;
      if ($(this).attr("data-pattern")) if (!val.match($(this).attr("data-pattern"))) return false;
    });
  }
  return true;
}


//ui - show
function show_update() {
  if (data.con_cfg && data.con_data && data.con_live) {
   show();
   menu_show();
   spinner_show(false);
   toast_show("");
  }
}


function show(val = true) {
  if (val) {
    $("#container").removeClass("hide");
  } else {
    $("#container").addClass("hide");
  }
}


//ui - mode_screen
function mode_screen() {
  cfg.main.mode_screen = !cfg.main.mode_screen;
  if (cfg.main.mode_screen) {
    $("#container").addClass("screen");
  } else {
    $("#container").removeClass("screen");
  }
}


//ui - toasts
function toasts_show(txt) {
  txt = val_to_array(txt, false, ["", ""]);
  if (txt.length == 1) txt[1] = "";

  if (txt[0].indexOf("\n") !== -1) txt[0] = "<ul><li>" + txt[0].replace(/\n/g, "</li><li>") + "</li></ul>";
  txt[1] = txt[1].replace(/\n/g, "<br>");

  var tmp = $("#tmp_toasts").clone();
  tmp.removeAttr("id");
  tmp.find(".header").html(txt[1]);
  tmp.find(".body").html(txt[0]);

  tmp.fadeIn(300).delay(cfg.main.toasts_timeout*1000).fadeOut(400, function(){$(this).remove();}).appendTo('#toasts');
}


//ui - toast
var toast_timer;
function toast_show(txt = "", error = false, timeout = cfg.main.toast_timeout*1000) {
  txt = val_to_array(txt, false, ["", ""]);
  if (txt.length == 1) txt[1] = "";

  if (txt[0].indexOf("\n") !== -1) txt[0] = "<ul><li>" + txt[0].replace(/\n/g, "</li><li>") + "</li></ul>";
  txt[1] = txt[1].replace(/\n/g, "<br>");

  if (txt[0] == "" && txt[1] == "") {
    $("#toast").removeClass("active");
  } else {
    var tmp = $("#tmp_toast").clone();
    tmp.removeAttr("id");
    var header = tmp.find(".header");
    header.html(txt[1]);
    if (error) {
      header.addClass("error");
      if (cfg_main.msg_btn_error) {
        var btn = $("#tmp_toast_button").clone();
        btn.removeAttr("id");
        btn.click(function() { toast_show(); });
        header.append(btn);
      }
    } else {
      header.removeClass("error");
      if (cfg_main.msg_btn) {
        var btn = $("#tmp_toast_button").clone();
        btn.removeAttr("id");
        btn.click(function() { toast_show(); });
        header.append(btn);
      }
    }
    var body = tmp.find(".body");
    body.html(txt[0]);
    $("#toast").html(tmp);
    $("#toast").addClass("active");
    clearTimeout(toast_timer);
    if (timeout > 0) toast_timer = setTimeout(function(){ $("#toast").removeClass("active"); }, timeout);
  }
}


function toast_confirm_show(field, callback) {
  var tmp = $("#tmp_toast_confirm").clone();
  tmp.removeAttr("id");

  attr_vs(field, ["off=Abort", "on=OK"]);

  var header = tmp.find(".header");
  if (field.msg) header.html(field.msg);
  if (field.i) header.prepend(add_icon_inline(field.i));
  if (cfg_main.msg_btn_confirm) {
    var btn = $("#tmp_toast_button").clone();
    btn.removeAttr("id");
    btn.click(function() {
      $("#toast_confirm").removeClass("active");
      $("#toast_confirm_overlay").removeClass("active");
      toast_show(field.msgs[0]);
    });
    header.append(btn);
  }

  var btn_ok = tmp.find(".btn-ok");
  var btn_abort = tmp.find(".btn-abort");

  btn_ok.html(field.vs[1][1]);
  btn_abort.html(field.vs[0][1]);

  attr_is(field);
  if (field.is) {
    btn_ok.prepend(add_icon_inline(field.is[1]));
    btn_abort.prepend(add_icon_inline(field.is[0]));
  }

  attr_msgs(field);

  btn_ok.click(function() {
    $("#toast_confirm").removeClass("active");
    $("#toast_confirm_overlay").removeClass("active");
    toast_show(field.msgs[1]);
    if (typeof callback === 'function') callback();
  });

  btn_abort.click(function() {
    $("#toast_confirm").removeClass("active");
    $("#toast_confirm_overlay").removeClass("active");
    toast_show(field.msgs[0]);
  });

  $("#toast_confirm").html(tmp);
  $("#toast_confirm").addClass("active");
  $("#toast_confirm_overlay").addClass("active");
}


//ui - popup
function popup_show(i) {
  if (isNaN(parseInt(i))) {
    i = $("[data-popup_name=" + i + "]").attr("data-popup");
    if (!i) return;
  }

  $("#popup_overlay").addClass("active");
  $("[data-type=popup]").each(function() {
    $(this).removeClass("active");
  });
  $("[data-popup=" + i + "]").addClass("active");
}


function popup_close() {
  $("#popup_overlay").removeClass("active");
  $("[data-type=popup]").each(function() {
    $(this).removeClass("active");
  });
}


//ui - state
function state_show(val = true) {
  if (val) {
    $("#state").addClass("ok");
    $("#state").removeClass("error");
  } else {
    $("#state").addClass("error");
    $("#state").removeClass("ok");
  }
}


//ui - spinner
function spinner_show(val = true) {
  if (val) {
    $("#spinner").removeClass("hide");
  } else {
    $("#spinner").addClass("hide");
  }
}


function spinner_update(uid = "", add = true) {
  uid = String(uid);
  if (uid != "") {
    var i = uids.indexOf(uid);
    if (i !== -1) {
      uids.splice(i, 1);
    }
    else if (add) {
      uids.push(uid);
    }
  }
  if (uids.length == 0) {
    spinner_show(false);
  } else {
    spinner_show(true);
  }
}


//ui - slide
const ui = document.querySelector(".ui-slide");
let ui_x = null, ui_y = null, ui_locked = false, ui_width, ui_height;


function ui_unify(e) { return e.changedTouches ? e.changedTouches[0] : e; }


function hasIroClass(classList) {
    for (var i = 0; i < classList.length; i++) {
        var element = classList[i];
        if (element.startsWith("Iro")) return true;
    }
    return false;
}


function ui_lock(e) {
  var l = e.target.classList;
  var pl = e.target.parentElement.classList;
  if (l.contains("no-slide") || hasIroClass(l) || hasIroClass(pl)) return;
  ui_locked = true;
  ui_x = ui_unify(e).clientX;
  ui_y = ui_unify(e).clientY;
}


function ui_move(e) {
  if (!ui_locked) return;
  if (cfg.main.slide_tab) {
    var clientX = ui_unify(e).clientX;
    var dx = clientX - ui_x;
    var s = Math.sign(dx);
    var f = +(s*dx/ui_width).toFixed(2);
    if ((clientX != 0) && f > cfg.main.slide_tab_area_ratio) tab_switch(s, ui_x);
    ui_locked = false;
    ui_x = null;
  }
  
  if (cfg.main.slide_menu) {
    var clientY = ui_unify(e).clientY;
    var dy = clientY - ui_y;
    var s = Math.sign(dy);
    var f = +(s*dy/ui_height).toFixed(2);
    if ((clientY != 0) && f > cfg.main.slide_menu_area_ratio) {
      if (s == 1) {
        menu_switch(s, ui_y);
      }
      else {
        menu_switch(s, ui_height - ui_y);
      }
    }
    ui_locked = false;
    ui_y = null;
  }
}


function ui_size() { ui_width = window.innerWidth; ui_height = window.innerHeight; }


ui_size();


window.addEventListener("resize", ui_size, false);
ui.addEventListener("mousedown", ui_lock, false);
ui.addEventListener("touchstart", ui_lock, false);
ui.addEventListener("mouseout", ui_move, false);
ui.addEventListener("mouseup", ui_move, false);
ui.addEventListener("touchend", ui_move, false);


//uid
function uid() {
  return "" + (Math.floor(Math.random() * Date.now()))
}


//pwa
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function() {
    navigator.serviceWorker
      .register("sw.js")
      .then(res => console.log("service worker registered"))
      .catch(err => console.log("service worker not registered", err));
  });
}

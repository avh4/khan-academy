
<%@ page import="com.google.gdata.client.*" %>
<%@ page import="com.google.gdata.client.youtube.*" %>
<%@ page import="com.google.gdata.data.*" %>
<%@ page import="com.google.gdata.data.geo.impl.*" %>
<%@ page import="com.google.gdata.data.media.*" %>
<%@ page import="com.google.gdata.data.media.mediarss.*" %>
<%@ page import="com.google.gdata.data.youtube.*" %>
<%@ page import="com.google.gdata.data.extensions.*" %>
<%@ page import="com.google.gdata.util.*" %>
<%@ page import="java.io.IOException" %>
<%@ page import="java.io.File" %>
<%@ page import="java.net.URL" %>
<%@ page import="java.util.Hashtable" %>
<%@ page import="java.util.Vector" %>
<%@ page import="java.util.Enumeration" %>

<HEAD>
<TITLE>Khan Academy</TITLE>
<link rel="stylesheet" href="/stylesheet.css">
</HEAD>

<body spacing="0" bgcolor=white text="#000000" link="#006699" vlink="#5493B4">
<DIV class="titlebox"><table border=0 width="100%">
<tr>
<td align="left"><img src="/images/khan.GIF"></td>
<td align="right" valign="bottom" width="100%"><form action="https://www.paypal.com/cgi-bin/webscr" method="post">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="hidden" name="hosted_button_id" value="2439291">
<input type="image" src="https://www.paypal.com/en_US/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="">
<img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form>
</td>
<td><!-- Facebook Badge START --><a href="http://www.facebook.com/pages/Khan-Academy/159403248441" title="Khan Academy" target="_TOP"><img src="http://badge.facebook.com/badge/159403248441.3033.45409799.png" width="120" height="80" style="border: 0px;" /></a><br/><!-- Facebook Badge END --></td>
<td align="right"><img src="/images/righttitle.jpg"></td>
</tr>
</table></DIV>

<table>
<tr>
<td>
<object width="213" height="172" align="right"><param name="movie" value="http://www.youtube.com/v/p6l8-1kHUsA&hl=en_US&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/p6l8-1kHUsA&hl=en_US&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="213" height="172"></embed></object>The Khan Academy is a not-for-profit organization with the mission of providing a high quality education to anyone, anywhere.
<P>We have 1000+ videos on YouTube covering everything from basic arithmetic and algebra to differential equations, physics, chemistry, biology and 
finance which have been recorded by <A href="/faq.jsp">Salman Khan</A>.  <P>
<A href="http://www.khanacademy.org//downloads/factsheet_11_2009.pdf">Download</A> the Khan Academy factsheet.
You can also read more about the Khan Academy vision in this <A href="http://www.khanacademy.org/downloads/vision.pdf">document</A>.
<P>

<A href="http://www.techawards.org/laureates/stories/index.php?id=220">The Khan Academy and Salman Khan have received a 2009 Tech Award in Education<img src="/images/techawards.jpg" align="left"></A>. 
The Tech Awards is an international awards program that honors innovators from around the world who are applying technology to benefit humanity.
<P>
Sal has also developed a  
<A href="#" onClick="vWindow=window.open('http://www.khanacademy.org/authenticate.jsp','vWindow','toolbar=no,location=yes,directories=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=660,height=600'); return false;"  ><B>free, adaptive math program available here</b>.</A>  
(
Keep in  mind that the web application is not fully supported and may not work properly with certain browser and/or network configurations)
<P>
To keep abreast of new videos as we add them, <A href="http://www.youtube.com/khanacademy" target="video_window" ><B>subscribe to the Khan Academy channel on YouTube.</B></A>
<P>
The entire video library is shown below.  Just click on a category or video title to start learning from the Khan Academy!
<P>
<%
try{



	YouTubeService service = new YouTubeService("ytapi-SalmanKhan-khanacademy-f04ltf18-0", "AI39si46SOSDkqp_OH7Hw9yz1J5xQH4CYicJPGFGfnoFQA3hNu_BU5Xy9-B1qTU5rw3C7iJBpSzdHuSNbmzZ-SjeiU5XnafUsw");

	String feedUrl = "http://gdata.youtube.com/feeds/api/users/khanacademy/uploads";

	feedUrl = "http://gdata.youtube.com/feeds/api/users/khanacademy/playlists"+"?start-index=1&max-results=50";

	PlaylistLinkFeed feed = service.getFeed(new URL(feedUrl), PlaylistLinkFeed.class);

	Vector colOne = new Vector();
	colOne.add("Brain Teasers");
	colOne.add("Current Economics");
	colOne.add("Banking and Money");
	colOne.add("Venture Capital and Capital Markets");
	colOne.add("Finance");
	colOne.add("Valuation and Investing");
	colOne.add("Credit Crisis");
	colOne.add("Geithner Plan");
	colOne.add("Paulson Bailout");
	
	
	
	
	Vector colTwo = new Vector();
	colTwo.add("Chemistry");
	colTwo.add("Arithmetic");
	colTwo.add("Pre-algebra");
	colTwo.add("Algebra");
	colTwo.add("California Standards Test: Algebra I"); 
	colTwo.add("California Standards Test: Algebra II");
	colTwo.add("Geometry");
	colTwo.add("California Standards Test: Geometry");
	
	
	Vector colThree = new Vector();
	colThree.add("Biology");
	colThree.add("Trigonometry");
	colThree.add("Precalculus");
	colThree.add("Statistics");
	colThree.add("Probability");
	colThree.add("Calculus");
	colThree.add("Differential Equations");
	
	
	
	Vector colFour = new Vector();
	
	
	colFour.add("Linear Algebra");
	colFour.add("Physics");
	
	
	%>
	<table width=100% border=0>
	<tr><td align=center>
	<%
		String firstDivider = "";
		Hashtable playlists = new Hashtable();
		for(PlaylistLinkEntry entry : feed.getEntries()) 
		{
			String pTitle = entry.getTitle().getPlainText();
			if (pTitle.compareTo("My Vlog")==0 || pTitle.compareTo("GMAT Data Sufficiency")==0 || pTitle.compareTo("GMAT: Problem Solving")==0 || pTitle.compareTo("Singapore Math")==0)
				continue;
			%><%=firstDivider%><A href="#<%=pTitle%>"><%=pTitle%></A><%
			firstDivider ="&nbsp;&nbsp;|&nbsp;&nbsp;";
			playlists.put(pTitle, entry.getFeedUrl());
		}
	%>
	</td>
	</tr>
	<table width=100% border=0>
	
	<tr><td valign=top width=25%>
		
		
		<div class="hdg"><A name="SAT Preparation"></a><h3>SAT Preparation</h3></div>
		<BR>
			<img src="http://ecx.images-amazon.com/images/I/5193F7Z7DFL._SS75_.jpg" align=left>
			We have taken all 8 math practice tests (432 problems)
			in "The Offical SAT Study Guide" by the College Board in 100+ videos ...
			<A href="/sat.jsp"   target="sub_videos">[More]</A>
		<P>
		<div class="hdg"><A name="GMAT Preparation"></a><h3>GMAT Preparation</h3></div>
		<BR>
			
			<img width="75" src="http://ecx.images-amazon.com/images/I/51EWCPF8VNL._SL160_AA115_.jpg" align=left>
			We have taken all 400+ data sufficiency and math problems 
			in "The Official Guide for GMAT Review" by the GMAC in 100+ videos below. ...
			<A href="/gmat.jsp"  target="sub_videos"  >[More]</A>
		
		<P>
		<div class="hdg"><A name="California Standards: Algebra II"></a><h3>California: Algebra II</h3></div>
		<BR>
			Sal has done all 80 problems from the Algebra II Standards Test (click to download) administered as part of the Standardized Testing and Reporting (STAR) Program under policies set by the State Board of Education.  ...
			<A href="/caalg2.jsp" target="sub_videos" >[More]</A>
		
			
			
		<P>
	<%
	Enumeration  colOneSubjects = colOne.elements();
	while(colOneSubjects.hasMoreElements())
	{
		String pTitle = (String)colOneSubjects.nextElement();
		%><div class="hdg"><A name="<%=pTitle%>"></a><h3><%=pTitle%></h3></div><%
		String pURL = (String)playlists.get(pTitle);
		
		for(int i=0; i<4; i++)
		{
			int startIndex = i*50+1;
			String playlistURL = pURL+"?start-index="+startIndex+"&max-results=50";
			PlaylistFeed playlistFeed = service.getFeed(new URL(playlistURL), PlaylistFeed.class);
	
	
	
			for(PlaylistEntry playlistEntry : playlistFeed.getEntries()) 
			{
				String summary = playlistEntry.getMediaGroup().getDescription().getPlainTextContent();
				%>
					<BR>
					<A href="<%=playlistEntry.getHtmlLink().getHref()%>" target="video_window"  title="<%=summary%>"><%=playlistEntry.getTitle().getPlainText()%></A>
				<%
			}
		}
		%><P><%
		
		
	}
	
	%></td><td valign=top>
	<%
	Enumeration  colTwoSubjects = colTwo.elements();
	while(colTwoSubjects.hasMoreElements())
	{
		String pTitle = (String)colTwoSubjects.nextElement();
		%><div class="hdg"><A name="<%=pTitle%>"></a><h3><%=pTitle%></h3></div><%
		String pURL = (String)playlists.get(pTitle);
		for(int i=0; i<4; i++)
		{
			int startIndex = i*50+1;
			String playlistURL = pURL+"?start-index="+startIndex+"&max-results=50";
			PlaylistFeed playlistFeed = service.getFeed(new URL(playlistURL), PlaylistFeed.class);
	
	
	
			for(PlaylistEntry playlistEntry : playlistFeed.getEntries()) 
			{
				String summary = playlistEntry.getMediaGroup().getDescription().getPlainTextContent();
				%>
					<BR>
					<A href="<%=playlistEntry.getHtmlLink().getHref()%>" target="video_window"  title="<%=summary%>"><%=playlistEntry.getTitle().getPlainText()%></A>
				<%
			}
		}
		%><P><%
	}
	
	%>
	
	
	
	</td><td valign=top>
	<%
	Enumeration  colThreeSubjects = colThree.elements();
	while(colThreeSubjects.hasMoreElements())
	{
		String pTitle = (String)colThreeSubjects.nextElement();
		%><div class="hdg"><A name="<%=pTitle%>"></a><h3><%=pTitle%></h3></div><%
		String pURL = (String)playlists.get(pTitle);
		for(int i=0; i<4; i++)
		{
			int startIndex = i*50+1;
			String playlistURL = pURL+"?start-index="+startIndex+"&max-results=50";
			PlaylistFeed playlistFeed = service.getFeed(new URL(playlistURL), PlaylistFeed.class);
	
	
	
			for(PlaylistEntry playlistEntry : playlistFeed.getEntries()) 
			{
				String summary = playlistEntry.getMediaGroup().getDescription().getPlainTextContent();
				%>
					<BR>
					<A href="<%=playlistEntry.getHtmlLink().getHref()%>" target="video_window"  title="<%=summary%>"><%=playlistEntry.getTitle().getPlainText()%></A>
				<%
			}
		}
		%><P><%
	}
	
	%>
	
	
	</td><td valign=top>
	<%
	Enumeration  colFourSubjects = colFour.elements();
	while(colFourSubjects.hasMoreElements())
	{
		String pTitle = (String)colFourSubjects.nextElement();
		%><div class="hdg"><A name="<%=pTitle%>"></a><h3><%=pTitle%></h3></div><%
		String pURL = (String)playlists.get(pTitle);
		for(int i=0; i<4; i++)
		{
			int startIndex = i*50+1;
			String playlistURL = pURL+"?start-index="+startIndex+"&max-results=50";
			PlaylistFeed playlistFeed = service.getFeed(new URL(playlistURL), PlaylistFeed.class);
	
	
	
			for(PlaylistEntry playlistEntry : playlistFeed.getEntries()) 
			{
				String summary = playlistEntry.getMediaGroup().getDescription().getPlainTextContent();
				%>
					<BR>
					<A href="<%=playlistEntry.getHtmlLink().getHref()%>" target="video_window"  title="<%=summary%>"><%=playlistEntry.getTitle().getPlainText()%></A>
				<%
			}
		}
	}
	
	%>
	
	<%
	/**
	int entryCount = 0;
	
	for(PlaylistLinkEntry entry : feed.getEntries()) 
	{
		String pTitle = entry.getTitle().getPlainText();	
		if (pTitle.compareTo("My Vlog")==0 || pTitle.compareTo("SAT Preparation")==0)
			continue;
		if (entryCount!=0)
		{
			%><P><%
		}
	%>
		
		<div class="hdg"><A name="<%=pTitle%>"></a><h3><%=pTitle%></h3></div>
		
	<%
		entryCount +=2;
		String playlistUrl = entry.getFeedUrl()+"?start-index=1&max-results=50";
		PlaylistFeed playlistFeed = service.getFeed(new URL(playlistUrl), PlaylistFeed.class);
		
		for(PlaylistEntry playlistEntry : playlistFeed.getEntries()) 
		{
			entryCount++;
			if (entryCount > 225)
			{
			entryCount=0;
				%></td><td valign=top>
				<div class="hdg"><h3><%=pTitle%> (continued...)</h3></div><%
			}
			String summary = playlistEntry.getMediaGroup().getDescription().getPlainTextContent();
		%>
		<BR>
		<A href="<%=playlistEntry.getHtmlLink().getHref()%>" target="video_window"  title="<%=summary%>"><%=playlistEntry.getTitle().getPlainText()%></A>
		<%
		}
		
		playlistUrl = entry.getFeedUrl()+"?start-index=51&max-results=50";
		playlistFeed = service.getFeed(new URL(playlistUrl), PlaylistFeed.class);
		
		for(PlaylistEntry playlistEntry : playlistFeed.getEntries()) 
		{
			entryCount++;
			if (entryCount > 225)
			{
			entryCount=0;
				%></td><td valign=top>
				<div class="hdg"><h3><%=pTitle%> (continued...)</h3></div><%
			}
			String summary = playlistEntry.getMediaGroup().getDescription().getPlainTextContent();
		%>
		<BR>
		<A href="<%=playlistEntry.getHtmlLink().getHref()%>" target="video_window"  title="<%=summary%>"><%=playlistEntry.getTitle().getPlainText()%></A>
		<%
		}
		
		playlistUrl = entry.getFeedUrl()+"?start-index=101&max-results=50";
		playlistFeed = service.getFeed(new URL(playlistUrl), PlaylistFeed.class);
		
		for(PlaylistEntry playlistEntry : playlistFeed.getEntries()) 
		{
			entryCount++;
			if (entryCount > 225)
			{
			entryCount=0;
				%></td><td valign=top>
				<div class="hdg"><h3><%=pTitle%> (continued...)</h3></div><%
			}
			String summary = playlistEntry.getMediaGroup().getDescription().getPlainTextContent();
		%>
		<BR>
		<A href="<%=playlistEntry.getHtmlLink().getHref()%>" target="video_window"  title="<%=summary%>"><%=playlistEntry.getTitle().getPlainText()%></A>
		<%
		}
		

	} *****/
	%></td></tr></table><%
 
    }catch(Exception e) {
      %><%=e%><%
    }
%>

</td>
<td width=200 valign=top>
<div class="highlightHeader">
			CNN: Sal on the Credit Crisis
		</div><div class="highlightBox">
		<A href="http://www.youtube.com/watch?v=_ZAlj2gu0eM" target="video_window"  >
		<img src="http://i4.ytimg.com/vi/_ZAlj2gu0eM/default.jpg" align=left> Sal appears on the Rick Sanchez show to explain the Credit Crisis </A> 
		<P>
		This appearance has led to a paper that Sal has co-authored with Berkeley professor Dr. David Leibweber on a solution to unfreezing credit 
		markets which is available
		<A href="http://cift.haas.berkeley.edu/nabi-intro.html" target="video_window">here</a>.
		
		
</div>
<P>
<div class="highlightHeader">
			About Salman Khan
		</div><div class="highlightBox">
		<img src="/images/salimransmall.JPG" align=left width=80> Salman Khan (Sal) founded the Khan Academy with the goal of using technology to educate the world
		<P>
		Sal received his MBA from Harvard Business School. He also holds a Masters in electrical engineering and computer science, a BS in electrical engineering and computer science, and a BS in mathematics from the Massachusetts Institute of Technology. <A href="/faq.jsp">Frequently Asked Questions</a>.
		
		
</div>
<P>
<div class="highlightHeader">
			What people are saying...
		</div><div class="highlightBox">
			"...My eldest kid is dancing around in my room here because she is so excited that she finally found someone that teaches like this. You're awesome. Thank you."
			<P>
			"I don't know who you are but in my mind you are a savior.  My children
			really struggle with math, there is an inherited learning disability
			in my family.  They get it but only after seeing it done multiple
			times.  Your videos will allow us to help our children get caught up
			with their peers.  As a parent I have to say, Thank You Thank You
			Thank You."
			<P>
			"I've never been very successful with algebra, I know this is pretty
			basic, but I have almost no comprehension of mathematics. I was
			honestly going to be kicked out of school for being non-productive, I
			was ready to be thrown out, but now I get this. Thank you so much..."
			<P>
			"This is my first year in college and until today i was completely lost
			in math. Half an hour with your presentations taught me more than
			three months of sitting in my professors class. You seriously saved my
			grade."
			<P>
			"Thank you so much! Keep up the good work :-D
			This is the most useful channel I've come across on youtube ever! Greetings from Denmark!"
			<P>
			"You're the only math tutor that makes sense to me. Most other ones
			seem to be speaking some sort of alien math language I cannot
			understand, assuming I already know formulas and all that. Thanks for
			keeping it simple and easy."
			<P>
			"You are my savior!
			I took the SATs during the beginning of the school year and pulled off
			a 750 in the math part. THANKS TO YOU!!..."
			<P>
			"You are a living legend as appealing to teaching that is :)"
			<P>
			"hmmh....With you around...Do I really need to go to math class now?"
			<P>
			"Sal, I just wanted to say thank you for all your help. It is
			marvellous that someone like yourself gives your time to help better
			others. This is especially true as you are helping so many people who
			you do not know. If only there were more people like you in the world.
			I'm studying physics and I am brushing up on some of my maths skills.
			You have been a great help to me, and I'm sure many others like me. I
			am just regretful that I have nothing to offer you in way of a thank
			you other than this message. If I ever come in to position where I may
			be able to help, you will undoubtedly hear from me."
			<P>
			"Thanks for educating all of us who're interested on mathematical
			knowledge. Thanks to you I finally see a light at the end of the
			tunnel. You're the best. Keep up the good work. If I were an engineer
			already, I'd donate money to you for this. I'm not going to forget
			Khan's academy."
			<P>
			"...I just wanted to say that out of every internet
			learning site I have used yours is by far the best!
			The maths [are] just so beautifully explained. Thank you so much; now I
			really think I will pass my maths exams~!"
			<P>
			"...Your videos have become very popular in my school, and my
			grades have sky-rocketed ever since I became accustomed to your
			methods of teaching..."
			<P>
			"...Before stumbling across your video's i had no idea how to relate with
			math problems [math is my extreme weak point] but after watching some of your video's, I can
			do math without a problem..."
			<P>
			"Thanks so much for your videos, there are immensely helpful. I have
			got my entire AP Calculus class watching your videos. :)"
			<P>
			"I am a high school Math/Physics Teacher working in Toronto Ontario. I
			have been referring students to your videos for the past year and have
			referenced many of them on my website. Those that have used it find it
			very useful, and have commented that you explain content better than I
			do..."
			<P>
			"I've been re-teaching myself physics with your videos, and I'd like
			you to know that you are miles better at keeping my attention than any
			physics or mathematics professor I had during my university work (and
			I say that while I'm working on my third degree). I only hope Youtube is still around when I have children so I can use
			these videos for them as well."
			<P>
		</div>
			
	
						

</td>
</tr>
</table>
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-6742635-1");
pageTracker._trackPageview();
} catch(err) {}</script>
</body>

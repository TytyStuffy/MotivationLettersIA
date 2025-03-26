# To know more about the Task class, visit: https://docs.crewai.com/concepts/tasks
from crewai import Task
from textwrap import dedent


class CustomTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

    def task_1_name(self, agent, var1, var2):
        return Task(
            description=dedent(
                f"""
            Do something as part of task 1
            
            {self.__tip_section()}
    
            Make sure to use the most recent data as possible.
    
            Use this variable: {var1}
            And also this variable: {var2}
        """
            ),
            expected_output="The expected output of the task",
            agent=agent,
        )

    def task_2_name(self, agent):
        return Task(
            description=dedent(
                f"""
            Take the input from task 1 and do something with it.
                                       
            {self.__tip_section()}

            Make sure to do something else.
        """
            ),
            expected_output="The expected output of the task",
            agent=agent,
        )

    def scrape_parcoursup(self, agent, parcoursup_url):
        return Task(
            description=dedent(
                f"""
            Extract all relevant information from the Parcoursup link about the educational program.
            
            Focus on:
            1. Program name and description
            2. Required qualifications and prerequisites
            3. Expected skills and qualities they're looking for in candidates
            4. Any specific admission criteria mentioned
            5. Program objectives and outcomes
            
            URL to analyze: {parcoursup_url}
            
            {self.__tip_section()}
            
            Be thorough and extract all details that would be useful for crafting a personalized 
            motivation letter. Format your findings in a clear, structured way.
        """
            ),
            expected_output="A comprehensive report of all relevant information about the educational program from Parcoursup.",
            agent=agent,
        )

    def scrape_etablissement(self, agent, etablissement_url):
        return Task(
            description=dedent(
                f"""
            Research and extract detailed information about the educational program from the institution's website.
            
            Focus on:
            1. Institution's values, mission and vision
            2. Unique aspects of the program that aren't mentioned on Parcoursup
            3. Faculty highlights or special resources
            4. Notable alumni or success stories
            5. Any specific projects, internships, or international opportunities
            6. The institution's culture and environment
            
            URL to analyze: {etablissement_url}
            
            {self.__tip_section()}
            
            Look for information that would allow the applicant to demonstrate specific knowledge about 
            the institution and program, showing that they've done their research.
        """
            ),
            expected_output="A detailed report with specific information about the program and institution that would make a motivation letter more targeted and compelling.",
            agent=agent,
        )

    def interact_with_user(self, agent, parcoursup_info, etablissement_info):
        return Task(
            description=dedent(
                f"""
            Conduct an interview with the student to gather personal information needed for their motivation letter.
            
            Use the information already collected about the program to ask relevant questions:
            
            Program information:
            {parcoursup_info}
            
            Institution information:
            {etablissement_info}
            
            Ask questions about:
            1. Academic background and achievements
            2. Relevant skills and experiences
            3. Why they're interested in this specific program
            4. How this program aligns with their career goals
            5. Personal qualities that make them a good fit
            6. Specific projects, experiences or achievements that demonstrate their passion
            7. Any challenges they've overcome that demonstrate their determination
            
            {self.__tip_section()}
            
            Be conversational and adapt your questions based on their responses. Dig deeper when you 
            identify areas that could strengthen their motivation letter.
        """
            ),
            expected_output="A comprehensive profile of the student with all relevant information needed to craft a personalized motivation letter.",
            agent=agent,
        )

    def generate_letter_version1(self, agent, parcoursup_info, etablissement_info, student_info):
        return Task(
            description=dedent(
                f"""
            Create a formal, structured motivation letter for the student based on all collected information.
            
            Program information:
            {parcoursup_info}
            
            Institution information:
            {etablissement_info}
            
            Student profile:
            {student_info}
            
            Your letter should:
            1. Follow a traditional, professional format
            2. Clearly demonstrate how the student meets the program requirements
            3. Highlight academic achievements and relevant experiences
            4. Connect the student's background with the program's objectives
            5. Be well-structured with an introduction, body paragraphs, and conclusion
            6. Use formal language while still being personalized
            
            {self.__tip_section()}
            
            The letter should be approximately 3500-4500 characters and written in French.
            Focus on creating a compelling case for why this student is qualified for and will succeed in this program.
        """
            ),
            expected_output="A complete, formal motivation letter in French that effectively presents the student's qualifications and fit for the program.",
            agent=agent,
        )

    def generate_letter_version2(self, agent, parcoursup_info, etablissement_info, student_info):
        return Task(
            description=dedent(
                f"""
            Create an engaging, story-driven motivation letter for the student based on all collected information.
            
            Program information:
            {parcoursup_info}
            
            Institution information:
            {etablissement_info}
            
            Student profile:
            {student_info}
            
            Your letter should:
            1. Begin with an attention-grabbing introduction
            2. Tell a compelling narrative about the student's journey
            3. Use vivid examples and specific anecdotes
            4. Showcase the student's passion and unique qualities
            5. Demonstrate clear knowledge of the program while maintaining a personal tone
            6. End with a memorable conclusion
            
            {self.__tip_section()}
            
            The letter should be approximately 3500-4500 characters and written in French.
            Focus on creating an authentic, memorable letter that reveals the person behind the application.
        """
            ),
            expected_output="A complete, creative motivation letter in French that tells a compelling story while effectively demonstrating the student's fit for the program.",
            agent=agent,
        )

    def fusion_letter(self, agent, letter1, letter2):
        return Task(
            description=dedent(
                f"""
            Analyze both motivation letter versions and create an optimized final version.
            
            Letter Version 1:
            {letter1}
            
            Letter Version 2:
            {letter2}
            
            Your task:
            1. Identify the strengths of each letter
            2. Compare how each letter addresses the program requirements and student qualities
            3. Select the most effective structure, tone, and approach
            4. Combine the best elements from both letters
            5. Ensure the final letter is cohesive, compelling, and authentic
            6. Check for any gaps or missed opportunities in both original versions
            
            {self.__tip_section()}
            
            Create a polished, final letter (in French) that maximizes the student's chances of admission
            by incorporating the best of both approaches. The final letter should be approximately 3500-4500 
            characters and read as a cohesive whole, not as disjointed pieces.
        """
            ),
            expected_output="A final, optimized motivation letter in French that combines the strengths of both previous versions.",
            agent=agent,
        )
